"""Entrypoint do serviço de agendamento (US-19).

Roda em container dedicado (separado do consumer RabbitMQ) com um
BlockingScheduler, garantindo uma única instância do job mesmo que o worker
consumer seja escalado horizontalmente.
"""
import os
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optio.settings')

import django
django.setup()

from apscheduler.schedulers.blocking import BlockingScheduler

from notifications import notify_users, process_saved_alerts

logging.basicConfig(
    level=os.getenv('WORKER_LOG_LEVEL', 'INFO'),
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger('optio.scheduler')

# Job 1 — preferências por área (cron semanal)
CRON_DAY_OF_WEEK = os.getenv('NOTIFY_CRON_DAY_OF_WEEK', 'mon')
CRON_HOUR = os.getenv('NOTIFY_CRON_HOUR', '8')
CRON_MINUTE = os.getenv('NOTIFY_CRON_MINUTE', '0')
TIMEZONE = os.getenv('NOTIFY_TIMEZONE', 'America/Sao_Paulo')

# Job 2 — alertas salvos (intervalo; default semanal, ajustável p/ testes)
ALERTS_INTERVAL_SECONDS = int(os.getenv('ALERTS_INTERVAL_SECONDS', str(7 * 24 * 60 * 60)))


def main() -> None:
    scheduler = BlockingScheduler(timezone=TIMEZONE)
    scheduler.add_job(
        notify_users,
        trigger='cron',
        day_of_week=CRON_DAY_OF_WEEK,
        hour=CRON_HOUR,
        minute=CRON_MINUTE,
        id='notify_new_courses',
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        process_saved_alerts,
        trigger='interval',
        seconds=ALERTS_INTERVAL_SECONDS,
        id='process_saved_alerts',
        max_instances=1,
        coalesce=True,
    )
    logger.info(
        'Scheduler iniciado. preferencias_cron=%s %s:%s alertas_interval_s=%s tz=%s',
        CRON_DAY_OF_WEEK, CRON_HOUR, CRON_MINUTE, ALERTS_INTERVAL_SECONDS, TIMEZONE,
    )
    scheduler.start()


if __name__ == '__main__':
    main()
