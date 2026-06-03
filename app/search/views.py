from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from datetime import timedelta

import logging
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from search.models import Course, Favorite, SearchRequest

from .choices import SearchStatus
from .forms import SearchRequestForm
from .publisher import QueuePublishError, publish_search_request


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

                logger.exception(
                    "Falha ao publicar SearchRequest %s na fila.",
                    search_request.id,
                )

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

    return render(
        request,
        "search/search_request_form.html",
        {"form": form},
    )


@login_required
def search_list(request):
    searches = SearchRequest.objects.filter(user=request.user)

    status_filter = request.GET.get('status')
    if status_filter:
        searches = searches.filter(status=status_filter)

    return render(request, 'search/search_list.html', {
        'searches': searches,
        'current_filter': status_filter,
    })


@login_required
def search_results(request, pk):
    search_request = get_object_or_404(SearchRequest, pk=pk, user=request.user)
    courses = Course.objects.filter(search_request=search_request)

    return render(request, 'search/search_results.html', {
        'search_request': search_request,
        'courses': courses,
    })


@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related("course")

    return render(request, 'search/favorites_list.html', {
        'favorites': favorites,
    })


@require_http_methods(["POST"])
@login_required
def favorite_remove(request, pk):
    favorite = get_object_or_404(Favorite, pk=pk, user=request.user)
    favorite.delete()

    messages.success(request, "Curso removido dos favoritos.")
    return redirect("search:favorites_list")