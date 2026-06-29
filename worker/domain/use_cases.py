import logging

from domain.contracts import DigestSection, SearchRequestedEvent
from search.choices import SearchStatus

logger = logging.getLogger("optio.worker.domain")


class SearchProcessor:
    """Busca manual (consumer): processa um evento da fila do início ao fim."""

    def __init__(self, repository, notifier, finder):
        self.repository = repository
        self.notifier = notifier
        self.finder = finder

    def process(self, event: SearchRequestedEvent) -> None:
        search_id = event.search_request_id
        logger.info(
            "Nova solicitação de busca. search_id=%s keywords=%r", search_id, event.keywords
        )

        self.repository.mark_search_status(search_id, SearchStatus.PROCESSING.value)

        courses = self.finder.find(event.criteria)

        if not courses:
            self.repository.mark_search_status(search_id, SearchStatus.NO_RESULTS.value, results_count=0)
            self.notifier.send_no_results(event.notification_email, search_id, event.keywords)
            logger.info("Busca concluída sem resultados. search_id=%s", search_id)
            return

        saved = self.repository.save_courses(search_id, courses)
        self.repository.mark_search_status(search_id, SearchStatus.COMPLETED.value, results_count=saved)
        self.notifier.send_results(event.notification_email, courses, search_id)
        logger.info("Busca concluída com sucesso. search_id=%s results=%d", search_id, saved)


class PreferenceNotifier:
    """Job: notificação por preferências de área. Busca compartilhada por grupo
    (área, modalidade); deduplica e notifica cada usuário do grupo."""

    def __init__(self, finder, repository, notifier):
        self.finder = finder
        self.repository = repository
        self.notifier = notifier

    def run(self) -> None:
        groups = self.repository.preference_groups()
        logger.info("Preferências: %d grupos (área, modalidade) a processar.", len(groups))

        emails_sent = 0
        for group in groups:
            try:
                courses = self.finder.find(group.criteria)
                if not courses:
                    continue
                for recipient in group.recipients:
                    try:
                        new_courses = self.repository.filter_new(recipient.id, courses)
                        if not new_courses:
                            continue
                        self.notifier.send_new_courses(recipient.email, new_courses)
                        self.repository.record_sent(recipient.id, new_courses)
                        emails_sent += 1
                    except Exception:
                        logger.exception("Falha ao notificar usuário. email=%s", recipient.email)
            except Exception:
                logger.exception("Falha ao processar grupo. criteria=%s", group.criteria)

        logger.info("Job de preferências concluído. emails_enviados=%d", emails_sent)


class AlertNotifier:
    """Job: alertas salvos. Verifica os alertas ativos por usuário e envia um
    digest consolidado com os cursos novos de todos os alertas do usuário."""

    def __init__(self, finder, repository, notifier):
        self.finder = finder
        self.repository = repository
        self.notifier = notifier

    def run(self) -> None:
        users = self.repository.users_with_active_alerts()
        logger.info("Alertas: %d usuários com alertas ativos.", len(users))

        digests_sent = 0
        for user_alerts in users:
            sections: list[DigestSection] = []
            seen: set[tuple[str, str]] = set()
            processed: list[int] = []

            for alert in user_alerts.alerts:
                try:
                    courses = self.finder.find(alert.criteria)
                    section_courses = []
                    for course in self.repository.filter_new(user_alerts.recipient.id, courses):
                        key = (course.name.strip().lower(), course.institution.strip().lower())
                        if key in seen:
                            continue
                        seen.add(key)
                        section_courses.append(course)
                    if section_courses:
                        sections.append(DigestSection(alert_name=alert.name, courses=section_courses))
                    processed.append(alert.id)
                except Exception:
                    logger.exception("Falha ao processar alerta. id=%s", alert.id)

            self.repository.mark_alerts_checked(processed)

            if not sections:
                continue
            try:
                self.notifier.send_alerts_digest(user_alerts.recipient.email, sections)
                self.repository.record_sent(
                    user_alerts.recipient.id,
                    [course for section in sections for course in section.courses],
                )
                digests_sent += 1
            except Exception:
                logger.exception("Falha no digest. email=%s", user_alerts.recipient.email)

        logger.info("Job de alertas concluído. digests_enviados=%d", digests_sent)
