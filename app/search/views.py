from django.shortcuts import redirect, render

# Create your views here.

import logging
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from search.models import SearchRequest

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
    """Lista todas as pesquisas do usuário."""
    searches = SearchRequest.objects.filter(user=request.user)

    # Filtro por status (opcional via query param)
    status_filter = request.GET.get('status')
    if status_filter:
        searches = searches.filter(status=status_filter)

    context = {
        'searches': searches,
        'current_filter': status_filter,
    }

    return render(request, 'search/search_list.html', context)