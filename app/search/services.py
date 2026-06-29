import os

from django.core.paginator import Paginator
from django.utils import timezone

from .choices import SearchStatus
from .models import Favorite, SavedAlert, SearchRequest
from .publisher import QueuePublishError, publish_search_request

PAGE_SIZE = 10

MAX_ACTIVE_ALERTS_PER_USER = int(os.getenv("MAX_ACTIVE_ALERTS_PER_USER", "3"))


def get_favorites(user, page: int):
    qs = Favorite.objects.filter(user=user).select_related("course")
    return Paginator(qs, PAGE_SIZE).get_page(page)


def get_search_history(user, filters: dict, page: int):
    qs = SearchRequest.objects.for_user(user).order_by("-created_at")

    if status := filters.get("status"):
        if status == "processing":
            qs = qs.filter(status__in=[SearchStatus.PENDING, SearchStatus.PROCESSING])
        else:
            qs = qs.filter(status=status)
    if q := filters.get("q"):
        qs = qs.filter(keywords__icontains=q)

    return Paginator(qs, PAGE_SIZE).get_page(page)


def delete_search(user, pk: int) -> None:
    search = SearchRequest.objects.get(pk=pk, user=user)
    search.is_deleted = True
    search.deleted_at = timezone.now()
    search.save(update_fields=["is_deleted", "deleted_at"])


def repeat_search(user, pk: int) -> tuple[SearchRequest, bool]:
    """Cria nova busca com os mesmos parâmetros. Retorna (busca, publicada)."""
    original = SearchRequest.objects.get(pk=pk, user=user)
    new_search = SearchRequest.objects.create(
        user=user,
        keywords=original.keywords,
        area=original.area,
        modality=original.modality,
        state=original.state,
        notification_email=original.notification_email,
        status=SearchStatus.PENDING,
    )
    try:
        publish_search_request(new_search)
    except QueuePublishError:
        new_search.status = SearchStatus.FAILED
        new_search.save(update_fields=["status"])
        return new_search, False
    return new_search, True


# ===== Alertas salvos =====

def _alert_name_from_keywords(keywords: str) -> str:
    name = keywords.strip()
    if len(name) > 120:
        name = name[:117] + "..."
    return (name[:1].upper() + name[1:]) if name else "Alerta"


def create_alert_from_search(user, data: dict) -> tuple[SavedAlert | None, str]:
    """Cria um SavedAlert a partir dos critérios de uma busca.

    Retorna (alerta, motivo). motivo ∈ {"created", "duplicate", "limit", "invalid"}.
    """
    keywords = (data.get("keywords") or "").strip()
    if not keywords:
        return None, "invalid"

    area = data.get("area", "") or ""
    modality = data.get("modality", "") or ""
    state = data.get("state", "") or ""

    duplicate = SavedAlert.objects.filter(
        user=user, active=True,
        keywords=keywords, area=area, modality=modality, state=state,
    ).exists()
    if duplicate:
        return None, "duplicate"

    active_count = SavedAlert.objects.filter(user=user, active=True).count()
    if active_count >= MAX_ACTIVE_ALERTS_PER_USER:
        return None, "limit"

    alert = SavedAlert.objects.create(
        user=user,
        name=_alert_name_from_keywords(keywords),
        keywords=keywords,
        area=area,
        modality=modality,
        state=state,
    )
    return alert, "created"


def toggle_alert(user, pk: int) -> tuple[SavedAlert, bool]:
    """Alterna o status ativo do alerta. Retorna (alerta, alterado).

    Ao ativar, respeita o teto de alertas ativos: se atingido, não altera
    e retorna alterado=False.
    """
    alert = SavedAlert.objects.get(pk=pk, user=user)
    if not alert.active:
        active_count = SavedAlert.objects.filter(user=user, active=True).count()
        if active_count >= MAX_ACTIVE_ALERTS_PER_USER:
            return alert, False
    alert.active = not alert.active
    alert.save(update_fields=["active", "updated_at"])
    return alert, True


def delete_alert(user, pk: int) -> None:
    SavedAlert.objects.get(pk=pk, user=user).delete()


def get_saved_alerts(user):
    return SavedAlert.objects.filter(user=user)
