import logging

from domain.contracts import JobRequest

logger = logging.getLogger("optio.worker.domain")


class SearchProcessor:
    """Busca manual (consumer): processa um evento da fila do início ao fim."""

    def __init__(self, publisher, finder):
        self.publisher = publisher
        self.finder = finder

    def process(self, request: JobRequest) -> None:
        logger.info("Iniciando scraping. job_id=%s tipo=%s", request.job_id, request.job_type)

        try:
            courses = self.finder.find(request.criteria)
            status = "COMPLETED" if courses else "NO_RESULTS"

            self.publisher.publish_result(
                job_id=request.job_id,
                job_type=request.job_type,
                status=status,
                courses=courses,
                email=request.notification_email,
                criteria=request.criteria.model_dump()
            )
            logger.info("Scraping concluído. cursos_encontrados=%d", len(courses) if courses else 0)
        except Exception as e:
            logger.exception("Erro no scraping. job_id=%s", request.job_id)
            self.publisher.publish_result(
                job_id=request.job_id,
                job_type=request.job_type,
                status="FAILED",
                email=request.notification_email,
                criteria=request.criteria.model_dump()
            )
        