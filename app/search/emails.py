"""E-mails do app de busca. Reaproveita o helper único de core.emails."""
from django.conf import settings
from django.urls import reverse

from core.emails import EmailDeliveryError, send_html_email

__all__ = ['EmailDeliveryError', 'send_results_email', 'send_no_results_email']


def _absolute_url(view_name: str, **kwargs) -> str:
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    return f"{site_url}{reverse(view_name, kwargs=kwargs)}"


def send_results_email(user_email: str, courses: list[dict], search_id: int) -> None:
    send_html_email(
        subject='Resultados da sua busca no Optio',
        template='search/emails/results_email.html',
        context={
            'courses': courses,
            'search_id': search_id,
            'results_url': _absolute_url('search:search_results', pk=search_id),
        },
        to_email=user_email,
    )


def send_no_results_email(user_email: str, search_id: int, keywords: str = '') -> None:
    send_html_email(
        subject='Sua busca foi concluída - Optio',
        template='search/emails/no_results_email.html',
        context={
            'search_id': search_id,
            'keywords': keywords,
            'new_search_url': _absolute_url('search:request_create'),
        },
        to_email=user_email,
    )
