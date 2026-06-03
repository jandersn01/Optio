from django.core.paginator import Paginator
from django.utils import timezone

from .choices import SearchStatus
from .models import SearchRequest
from .publisher import QueuePublishError, publish_search_request

PAGE_SIZE = 10


def get_search_history(user, filters: dict, page: int):
    qs = SearchRequest.objects.for_user(user).order_by("-created_at")

    if status := filters.get("status"):
        qs = qs.filter(status=status)
    if area := filters.get("area"):
        qs = qs.filter(area=area)
    if modality := filters.get("modality"):
        qs = qs.filter(modality=modality)
    if state := filters.get("state"):
        qs = qs.filter(state=state)

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
