"""Infra de e-mail compartilhada do projeto.

`send_html_email` é o único ponto que renderiza um template e envia o e-mail,
convertendo qualquer falha em `EmailDeliveryError`. As funções específicas (aqui
e em search.emails) apenas montam assunto/template/contexto.
"""
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext

logger = logging.getLogger(__name__)


class EmailDeliveryError(Exception):
    pass


def send_html_email(*, subject: str, template: str, context: dict, to_email: str) -> None:
    if not to_email:
        raise EmailDeliveryError('E-mail do destinatário não informado.')
    try:
        html_content = render_to_string(template, context)
        message = EmailMultiAlternatives(
            subject=subject,
            body=strip_tags(html_content),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        message.attach_alternative(html_content, 'text/html')
        message.send(fail_silently=False)
        logger.info('E-mail enviado. template=%s to=%s', template, to_email)
    except EmailDeliveryError:
        raise
    except Exception as error:
        logger.exception('Falha ao enviar e-mail. template=%s to=%s', template, to_email)
        raise EmailDeliveryError(
            f'Falha ao enviar e-mail ({template}) para {to_email}.'
        ) from error


def send_new_courses_email(user_email: str, courses: list[dict]) -> None:
    """E-mail de novos cursos (job de preferências). Não envia se a lista for vazia."""
    if not courses:
        return
    send_html_email(
        subject=gettext('Novos cursos para você no Optio'),
        template='core/emails/new_courses_email.html',
        context={'courses': courses},
        to_email=user_email,
    )


def send_alerts_digest_email(user_email: str, sections: list[dict]) -> None:
    """Digest consolidado dos alertas salvos. `sections` = [{'name', 'courses'}]."""
    if not sections:
        return
    total = sum(len(section['courses']) for section in sections)
    send_html_email(
        subject=gettext('Novidades nos seus alertas — Optio'),
        template='core/emails/alerts_digest_email.html',
        context={'sections': sections, 'total': total},
        to_email=user_email,
    )
