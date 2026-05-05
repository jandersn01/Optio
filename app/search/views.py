from django.shortcuts import redirect, render

# Create your views here.

import logging
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from .choices import SearchStatus
from .forms import SearchRequestForm
from .publisher import QueuePublishError, publish_search_request


logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def search_request_create(request):
    if request.method == "POST":
        form = SearchRequestForm(request.POST)

        if form.is_valid():
            search_request = form.save(commit=False)

            if request.user.is_authenticated:
                search_request.user = request.user

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

            return redirect("search:request_create")

    else:
        form = SearchRequestForm()

    return render(
        request,
        "search/search_request_form.html",
        {"form": form},
    )
