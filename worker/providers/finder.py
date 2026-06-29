"""Pipeline de descoberta de cursos: scrape → prompt → LLM → parse.

Único ponto que orquestra os providers. Reusado pelo consumer (busca manual,
via SearchProcessor) e pelos jobs de notificação (preferências/alertas), evitando
duplicação da pipeline.
"""
import logging

from domain.contracts import CourseData, SearchCriteria
from providers.scraper import search_courses_web
from providers.prompts import build_prompt
from providers.llm import call_llm, parse_llm_response

logger = logging.getLogger("optio.worker.finder")


class CourseFinder:
    def find(self, criteria: SearchCriteria) -> list[CourseData]:
        payload = criteria.model_dump()
        raw_content = search_courses_web(payload)
        prompt = build_prompt(payload, raw_content)
        parsed = parse_llm_response(call_llm(prompt))
        return [CourseData(**item) for item in parsed]
