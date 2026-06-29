import os
from collections import OrderedDict

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "optio.settings")
django.setup()

from django.utils import timezone

from core.models import NotificationPreference, NotificationSent
from search.models import Course, SavedAlert, SearchRequest

from domain.contracts import (
    AlertSpec,
    CourseData,
    PreferenceGroup,
    Recipient,
    SearchCriteria,
    UserAlerts,
)
from domain.exceptions import SearchNotFoundError


class SearchRepository:
    """Persistência da busca manual (consumer)."""

    def _get_or_raise(self, search_id: int) -> SearchRequest:
        search_request = SearchRequest.objects.filter(id=search_id).first()
        if not search_request:
            raise SearchNotFoundError(f"SearchRequest {search_id} não encontrada.")
        return search_request

    def mark_search_status(self, search_id: int, status: str, results_count: int | None = None) -> None:
        search_request = self._get_or_raise(search_id)
        update_fields = ["status"]
        search_request.status = status
        if results_count is not None:
            search_request.results_count = results_count
            update_fields.append("results_count")
        search_request.save(update_fields=update_fields)

    def save_courses(self, search_id: int, courses: list[CourseData]) -> int:
        search_request = self._get_or_raise(search_id)
        Course.objects.bulk_create([
            Course(
                search_request=search_request,
                name=c.name,
                institution=c.institution,
                modality=c.modality,
                state=c.state,
                link=c.link,
            )
            for c in courses
        ])
        return len(courses)


class NotificationRepository:
    """Acesso a dados dos jobs de notificação (preferências, alertas, dedup)."""

    def preference_groups(self) -> list[PreferenceGroup]:
        """Agrupa preferências ativas por (área, modalidade). Preferências sem área
        são ignoradas (não há keyword para buscar)."""
        groups: "OrderedDict[tuple[str, str], list[Recipient]]" = OrderedDict()
        prefs = NotificationPreference.objects.filter(active=True).select_related("user")
        for pref in prefs:
            recipient = Recipient(id=pref.user_id, email=pref.user.email)
            for area in pref.area_list:
                groups.setdefault((area, pref.modality or ""), []).append(recipient)
        return [
            PreferenceGroup(
                criteria=SearchCriteria(keywords=area, area=area, modality=modality),
                recipients=recipients,
            )
            for (area, modality), recipients in groups.items()
        ]

    def users_with_active_alerts(self) -> list[UserAlerts]:
        by_user: "OrderedDict[int, UserAlerts]" = OrderedDict()
        alerts = SavedAlert.objects.filter(active=True).select_related("user")
        for alert in alerts:
            entry = by_user.get(alert.user_id)
            if entry is None:
                entry = UserAlerts(
                    recipient=Recipient(id=alert.user_id, email=alert.user.email),
                    alerts=[],
                )
                by_user[alert.user_id] = entry
            entry.alerts.append(AlertSpec(
                id=alert.id,
                name=alert.name,
                criteria=SearchCriteria(
                    keywords=alert.keywords,
                    area=alert.area,
                    modality=alert.modality,
                    state=alert.state,
                ),
            ))
        return list(by_user.values())

    def filter_new(self, user_id: int, courses: list[CourseData]) -> list[CourseData]:
        """Filtra os cursos ainda não notificados ao usuário, deduplicando também
        dentro da própria lista. Uma única query (sem N+1)."""
        unique: "OrderedDict[str, CourseData]" = OrderedDict()
        for course in courses:
            fingerprint = NotificationSent.fingerprint_for(course.name, course.institution)
            unique.setdefault(fingerprint, course)
        if not unique:
            return []
        already = set(
            NotificationSent.objects
            .filter(user_id=user_id, course_fingerprint__in=list(unique))
            .values_list("course_fingerprint", flat=True)
        )
        return [course for fingerprint, course in unique.items() if fingerprint not in already]

    def record_sent(self, user_id: int, courses: list[CourseData]) -> None:
        NotificationSent.objects.bulk_create(
            [
                NotificationSent(
                    user_id=user_id,
                    course_fingerprint=NotificationSent.fingerprint_for(c.name, c.institution),
                    course_name=c.name,
                    course_institution=c.institution,
                    course_link=c.link,
                )
                for c in courses
            ],
            ignore_conflicts=True,
        )

    def mark_alerts_checked(self, alert_ids: list[int]) -> None:
        if alert_ids:
            SavedAlert.objects.filter(id__in=alert_ids).update(last_checked_at=timezone.now())
