import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse


logger = logging.getLogger(__name__)


class EmailDeliveryError(Exception):
    pass


def send_results_email(user_email: str, courses: list[dict], search_id: int) -> None:
    if not user_email:
        raise EmailDeliveryError("E-mail do usuário não informado.")

    try:
        subject = "Resultados da sua busca no Optio"

        ##results_url = f"{settings.SITE_URL}/search/{search_id}/results/"
        
        site_url = getattr(settings, "SITE_URL", "http://localhost:8000")
        results_path = reverse('search:request_list')
        # Como ainda não temos uma tela de detalhe de resultados,
        # apontamos para a listagem de buscas do usuário.
        results_url = f"{site_url}{results_path}"


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
        message.send(fail_silently=False)
        
        logger.info(
            "E-mail de resultados enviado com sucesso. search_id=%s email=%s",
            search_id,
            user_email,
        )

    except Exception as error:
        logger.exception(
            "Falha ao preparar/enviar e-mail de resultados. search_id=%s email=%s",
            search_id,
            user_email,
        )
        raise EmailDeliveryError(
            f"Falha ao enviar e-mail da busca {search_id}."
        ) from error