import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse


logger = logging.getLogger(__name__)


class EmailDeliveryError(Exception):
    pass


def _absolute_url(view_name: str, **kwargs) -> str:
    site_url = getattr(settings, "SITE_URL", "http://localhost:8000")
    return f"{site_url}{reverse(view_name, kwargs=kwargs)}"


def _send_html_email(
    *,
    subject: str,
    template: str,
    context: dict,
    to_email: str,
    search_id: int,
) -> None:
    """Renderiza um template HTML e envia o e-mail, convertendo falhas em EmailDeliveryError."""
    if not to_email:
        raise EmailDeliveryError("E-mail do usuário não informado.")

    try:
        html_content = render_to_string(template, context)
        message = EmailMultiAlternatives(
            subject=subject,
            body=strip_tags(html_content),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        message.attach_alternative(html_content, "text/html")
        message.send(fail_silently=False)

        logger.info(
            "E-mail enviado. template=%s search_id=%s email=%s",
            template,
            search_id,
            to_email,
        )
    except Exception as error:
        logger.exception(
            "Falha ao enviar e-mail. template=%s search_id=%s email=%s",
            template,
            search_id,
            to_email,
        )
        raise EmailDeliveryError(
            f"Falha ao enviar e-mail da busca {search_id}."
        ) from error


def send_results_email(user_email: str, courses: list[dict], search_id: int) -> None:
    _send_html_email(
        subject="Resultados da sua busca no Optio",
        template="search/emails/results_email.html",
        context={
            "courses": courses,
            "search_id": search_id,
            "results_url": _absolute_url("search:search_results", pk=search_id),
        },
        to_email=user_email,
        search_id=search_id,
    )


def send_no_results_email(user_email: str, search_id: int, keywords: str = "") -> None:
    """Envia e-mail informando que nenhum curso foi encontrado."""
    _send_html_email(
        subject="Sua busca foi concluída - Optio",
        template="search/emails/no_results_email.html",
        context={
            "search_id": search_id,
            "keywords": keywords,
            "new_search_url": _absolute_url("search:request_create"),
        },
        to_email=user_email,
        search_id=search_id,
    )