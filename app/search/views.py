from datetime import timedelta

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext
from django.views.decorators.http import require_http_methods, require_POST

from search.models import Course, Favorite, SavedAlert, SearchRequest

from .choices import SearchArea, SearchModality, SearchStates_Br, SearchStatus
from .forms import SearchRequestForm
from .publisher import QueuePublishError, publish_search_request
from .services import (
    create_alert_from_search,
    delete_alert,
    delete_search,
    get_favorites,
    get_saved_alerts,
    get_search_history,
    max_active_alerts_for,
    repeat_search,
    toggle_alert,
)


logger = logging.getLogger(__name__)


def _safe_next(request, fallback="search:favorites_list"):
    """Retorna o destino de `next` apenas se for uma URL interna; senão, o fallback."""
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return fallback


@require_http_methods(["GET", "POST"])
@login_required
def search_request_create(request):
    if request.method == "POST":
        form = SearchRequestForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            if request.POST.get("save_as_alert"):
                alert, reason = create_alert_from_search(request.user, data)
                if reason == "created":
                    messages.success(
                        request,
                        gettext('Alerta "%(name)s" salvo. Avisaremos quando surgirem cursos novos.')
                        % {"name": alert.name},
                    )
                elif reason == "duplicate":
                    messages.info(
                        request,
                        gettext("Você já tem um alerta ativo com esses critérios."),
                    )
                elif reason == "limit":
                    messages.warning(
                        request,
                        gettext(
                            "Limite de %(max)s alertas ativos atingido. "
                            "A busca segue normalmente, mas o alerta não foi salvo."
                        ) % {"max": max_active_alerts_for(request.user)},
                    )

            cached = SearchRequest.objects.filter(
                user=request.user,
                keywords=data["keywords"],
                area=data.get("area", ""),
                modality=data.get("modality", ""),
                state=data.get("state", ""),
                status=SearchStatus.COMPLETED,
                created_at__gte=timezone.now() - timedelta(days=2),
            ).first()

            if cached:
                messages.info(
                    request,
                    gettext("Encontramos uma busca recente com os mesmos critérios. Exibindo resultados anteriores."),
                )
                return redirect("search:search_results", pk=cached.pk)

            search_request = form.save(commit=False)
            search_request.user = request.user
            search_request.notification_email = request.user.email
            search_request.status = SearchStatus.PENDING
            search_request.save()

            try:
                publish_search_request(search_request)
            except QueuePublishError:
                search_request.status = SearchStatus.FAILED
                search_request.save(update_fields=["status"])
                logger.exception("Falha ao publicar SearchRequest %s na fila.", search_request.id)
                messages.error(
                    request,
                    gettext("Não foi possível enviar sua busca para processamento. Tente novamente em alguns instantes."),
                )
                return redirect("search:request_create")

            messages.success(
                request,
                gettext("Busca recebida com sucesso. Os resultados serão processados em segundo plano."),
            )
            return redirect("search:request_list")

    else:
        form = SearchRequestForm()

    return render(request, "search/search_request_form.html", {
        "form": form,
        "example_chips": [
            "Engenharia de software",
            "Inteligência Artificial",
            "Ciência de dados",
            "Educação e docência",
        ],
    })


@login_required
def search_list(request):
    filters = {
        "status": request.GET.get("status", ""),
        "q": request.GET.get("q", ""),
    }
    page_obj = get_search_history(request.user, filters, request.GET.get("page", 1))

    all_qs = SearchRequest.objects.for_user(request.user)
    counts = {
        "all": all_qs.count(),
        "completed": all_qs.filter(status=SearchStatus.COMPLETED).count(),
        "processing": all_qs.filter(
            status__in=[SearchStatus.PENDING, SearchStatus.PROCESSING]
        ).count(),
        "no_results": all_qs.filter(status=SearchStatus.NO_RESULTS).count(),
    }

    return render(request, "search/search_list.html", {
        "page_obj": page_obj,
        "filters": filters,
        "counts": counts,
    })


@login_required
def search_results(request, pk):
    search_request = get_object_or_404(SearchRequest, pk=pk, user=request.user)
    
    if search_request.status == SearchStatus.PROCESSING:
        limite_tempo = search_request.created_at + timedelta(minutes=5)

        if timezone.now() > limite_tempo:
            search_request.status = SearchStatus.FAILED
            search_request.save(update_fields=['status'])
            
    courses = Course.objects.filter(search_request=search_request)
    favorite_map = {
        f.course_id: f.pk
        for f in Favorite.objects.filter(user=request.user, course__in=courses)
    }
    return render(request, "search/search_results.html", {
        "search_request": search_request,
        "courses": courses,
        "favorite_map": favorite_map,
    })


@login_required
@require_POST
def search_delete(request, pk):
    try:
        delete_search(request.user, pk)
        messages.success(request, gettext("Busca removida do histórico."))
    except SearchRequest.DoesNotExist:
        messages.error(request, gettext("Busca não encontrada."))
    return redirect("search:request_list")


@login_required
@require_POST
def search_repeat(request, pk):
    try:
        new_search, published = repeat_search(request.user, pk)
    except SearchRequest.DoesNotExist:
        messages.error(request, gettext("Busca não encontrada."))
        return redirect("search:request_list")

    if not published:
        messages.error(
            request,
            gettext("Não foi possível enviar sua busca para processamento. Tente novamente em alguns instantes."),
        )
        return redirect("search:request_list")

    messages.success(request, gettext("Busca repetida com sucesso."))
    return redirect("search:search_results", pk=new_search.pk)


@login_required
def favorites_list(request):
    page_obj = get_favorites(request.user, request.GET.get("page", 1))
    return render(request, "search/favorites_list.html", {"page_obj": page_obj})


@login_required
@require_POST
def favorite_add(request, pk):
    course = get_object_or_404(Course, pk=pk, search_request__user=request.user)
    try:
        Favorite.objects.create(user=request.user, course=course)
        messages.success(request, gettext('"%(name)s" salvo nos favoritos.') % {'name': course.name})
    except IntegrityError:
        messages.info(request, gettext("Curso já está nos seus favoritos."))
    return redirect(_safe_next(request))


@login_required
@require_POST
def favorite_remove(request, pk):
    # pk = course pk (não o pk do Favorite)
    favorite = get_object_or_404(Favorite, course_id=pk, user=request.user)
    course_name = favorite.course.name
    favorite.delete()
    messages.success(request, gettext('"%(name)s" removido dos favoritos.') % {'name': course_name})
    return redirect(_safe_next(request))


@login_required
def alerts_list(request):
    alerts = get_saved_alerts(request.user)
    active_count = sum(1 for a in alerts if a.active)
    return render(request, "search/alerts_list.html", {
        "alerts": alerts,
        "active_count": active_count,
        "max_alerts": max_active_alerts_for(request.user),
    })


@login_required
@require_POST
def alert_toggle(request, pk):
    try:
        alert, toggled = toggle_alert(request.user, pk)
    except SavedAlert.DoesNotExist:
        messages.error(request, gettext("Alerta não encontrado."))
        return redirect("search:alerts_list")

    if not toggled:
        messages.warning(
            request,
            gettext(
                "Você já tem %(max)s alertas ativos. Pause um antes de ativar outro."
            ) % {"max": max_active_alerts_for(request.user)},
        )
    elif alert.active:
        messages.success(request, gettext("Alerta ativado."))
    else:
        messages.success(request, gettext("Alerta pausado."))
    return redirect(_safe_next(request, fallback="search:alerts_list"))


@login_required
@require_POST
def alert_delete(request, pk):
    try:
        delete_alert(request.user, pk)
        messages.success(request, gettext("Alerta apagado."))
    except SavedAlert.DoesNotExist:
        messages.error(request, gettext("Alerta não encontrado."))
    return redirect("search:alerts_list")
