import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


logger = logging.getLogger(__name__)


class EmailDeliveryError(Exception):
    pass


def send_results_email(user_email: str, courses: list[dict], search_id: int) -> None:
    if not user_email:
        raise EmailDeliveryError("E-mail do usuário não informado.")

    subject = "Resultados da sua busca no Optio"

    results_url = f"{settings.SITE_URL}/search/{search_id}/results/"

    context = {
        "courses": courses,
        "search_id": search_id,
        "results_url": results_url,
    }

    html_content = render_to_string(
        "search/emails/results_email.html",
        context,
    )

    text_content = strip_tags(html_content)

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user_email],
    )

    message.attach_alternative(html_content, "text/html")

    try:
        message.send(fail_silently=False)

    except Exception as error:
        logger.exception(
            "Falha ao enviar e-mail de resultados da busca %s.",
            search_id,
        )
        raise EmailDeliveryError(
            f"Falha ao enviar e-mail da busca {search_id}."
        ) from error