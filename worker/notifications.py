"""Composition root dos jobs de notificação (chamado pelo scheduler).

Apenas monta as dependências concretas (infra/providers) e delega para as
use-cases do domínio. A lógica vive em domain.use_cases; a pipeline em
providers.finder — os mesmos reusados pelo consumer de busca manual.
"""
from infra.repositories import NotificationRepository
from infra.notifications import EmailNotificationService
from providers.finder import CourseFinder
from domain.use_cases import AlertNotifier, PreferenceNotifier


def notify_users() -> None:
    PreferenceNotifier(
        finder=CourseFinder(),
        repository=NotificationRepository(),
        notifier=EmailNotificationService(),
    ).run()


def process_saved_alerts() -> None:
    AlertNotifier(
        finder=CourseFinder(),
        repository=NotificationRepository(),
        notifier=EmailNotificationService(),
    ).run()
