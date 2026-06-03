from datetime import timedelta

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from search.models import Course, Favorite, SearchRequest

from .choices import SearchArea, SearchModality, SearchStates_Br, SearchStatus
from .forms import SearchRequestForm
from .publisher import QueuePublishError, publish_search_request
from .services import delete_search, get_search_history, repeat_search


logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
@login_required
def search_request_create(request):
    if request.method == "POST":
        form = SearchRequestForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
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
                    "Encontramos uma busca recente com os mesmos critérios. Exibindo resultados anteriores.",
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
                    "Não foi possível enviar sua busca para processamento. Tente novamente em alguns instantes.",
                )
                return redirect("search:request_create")

            messages.success(
                request,
                "Busca recebida com sucesso. Os resultados serão processados em segundo plano.",
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
        messages.success(request, "Busca removida do histórico.")
    except SearchRequest.DoesNotExist:
        messages.error(request, "Busca não encontrada.")
    return redirect("search:request_list")


@login_required
@require_POST
def search_repeat(request, pk):
    try:
        new_search, published = repeat_search(request.user, pk)
    except SearchRequest.DoesNotExist:
        messages.error(request, "Busca não encontrada.")
        return redirect("search:request_list")

    if not published:
        messages.error(
            request,
            "Não foi possível enviar sua busca para processamento. Tente novamente em alguns instantes.",
        )
        return redirect("search:request_list")

    messages.success(request, "Busca repetida com sucesso.")
    return redirect("search:search_results", pk=new_search.pk)


@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related("course")
    return render(request, "search/favorites_list.html", {"favorites": favorites})


@login_required
@require_POST
def favorite_add(request, pk):
    course = get_object_or_404(Course, pk=pk)
    try:
        Favorite.objects.create(user=request.user, course=course)
        messages.success(request, f'"{course.name}" salvo nos favoritos.')
    except IntegrityError:
        messages.info(request, "Curso já está nos seus favoritos.")
    return redirect(request.POST.get("next", "search:favorites_list"))


@login_required
@require_POST
def favorite_remove(request, pk):
    # pk = course pk (não o pk do Favorite)
    favorite = get_object_or_404(Favorite, course_id=pk, user=request.user)
    course_name = favorite.course.name
    favorite.delete()
    messages.success(request, f'"{course_name}" removido dos favoritos.')
    return redirect(request.POST.get("next", "search:favorites_list"))
