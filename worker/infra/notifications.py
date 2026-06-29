from search.emails import send_results_email, send_no_results_email
from core.emails import send_new_courses_email, send_alerts_digest_email

from domain.contracts import CourseData, DigestSection


class EmailNotificationService:
    """Adapter de e-mail sobre os helpers da app (search.emails / core.emails)."""

    # ── Busca manual (consumer) ──
    def send_no_results(self, user_email: str, search_id: int, keywords: str) -> None:
        send_no_results_email(user_email=user_email, search_id=search_id, keywords=keywords)

    def send_results(self, user_email: str, courses: list[CourseData], search_id: int) -> None:
        send_results_email(
            user_email=user_email,
            courses=[c.model_dump() for c in courses],
            search_id=search_id,
        )

    # ── Jobs de notificação ──
    def send_new_courses(self, user_email: str, courses: list[CourseData]) -> None:
        send_new_courses_email(user_email, [c.model_dump() for c in courses])

    def send_alerts_digest(self, user_email: str, sections: list[DigestSection]) -> None:
        send_alerts_digest_email(
            user_email,
            [
                {"name": section.alert_name, "courses": [c.model_dump() for c in section.courses]}
                for section in sections
            ],
        )
