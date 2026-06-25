import logging
from domain.exceptions import InvalidMessageError, SearchNotFoundError
from provideers.scraper import search_courses_web
from provides.prompts import build_prompt
from providers.llm import call_llm, parse_llm_response

logger = logging.getLogger("optio.worker.domain")

class SearchProcessor:
    def __init__(self, repository, notifier):
        self.repository = repository
        self.notifier = notifier
        
    def process(self, payload: dict) -> None:
        self._validate_payload(payload)
        
        search_id = payload["search_request_id"]
        user_email = payload["notification_email"]
        
        logger.info(
            "Nova solicitação de busca. search_id=%s keywords=%r area=%r modality=%r state=%r",
            search_id, payload.get("keywords"), payload.get("area"),
            payload.get("modality"), payload.get("state")
        )
        
        self.repository.mark_search_status(search_id, "PROCESSING")
        
        raw_content = search_courses_web(payload)
        prompt = build_prompt(payload, raw_content)
        llm_response = call_llm(prompt)
        courses_data = parse_llm_response(llm_response)
        
        if not courses_data:
            self.repository.mark_search_status(search_id, "NO_RESULTS", results_count=0)
            self.notifier.send_no_results(user_email, search_id, payload.get("keywords", ""))
            logger.info("Busca concluída sem resultados. search_id=%s", search_id)
            return
        
        saved_count = self.repository.save_courses(search_id, courses_data)
        self.repository.mark_search_status(search_id, "COMPLETED", results_count=saved_count)
        self.notifier.send_results_email(user_email, courses_data, search_id)
        logger.info("Busca concluída com sucesso. search_id=%s results=%d", search_id, saved_count)
        
        def _validate_payload(self, payload: dict) -> None:
            required_fields = ["type", "search_request_id", "user_id", "notification_email", "keywords"]
            missing = [f for f in required_fields if not payload.get(f)]
            if missing:
                raise InvalidMessageError(f"Campos obrigatórios ausentes: {', '.join(missing)}")
            if payload.get("type") != "search_requested":
                raise InvalidMessageError(f"Tipo de mensagem desconhecido: {payload.get('type')}")