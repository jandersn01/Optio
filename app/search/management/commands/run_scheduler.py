import os
import logging
from django.core.management.base import BaseCommand
from apscheduler.schedulers.blocking import BlockingScheduler
from search.tasks import dispatch_preferences, dispatch_saved_alerts, fail_stalled_searches

logger = logging.getLogger('optio.scheduler')

class Command(BaseCommand):
    help = 'Inicia o orquestrador de jobs em background do Django'

    def handle(self, *args, **options):
        TIMEZONE = os.getenv('NOTIFY_TIMEZONE', 'America/Sao_Paulo')
        ALERTS_INTERVAL = int(os.getenv('ALERTS_INTERVAL_SECONDS', 604800))

        CRON_DAY_OF_WEEK = os.getenv('NOTIFY_CRON_DAY_OF_WEEK', 'mon')
        CRON_HOUR = os.getenv('NOTIFY_CRON_HOUR', '8')
        CRON_MINUTE = os.getenv('NOTIFY_CRON_MINUTE', '0')
        
        scheduler = BlockingScheduler(timezone=TIMEZONE)
        
        scheduler.add_job(
            dispatch_saved_alerts,
            trigger='interval',
            seconds=ALERTS_INTERVAL,
            id='process_saved_alerts',
            max_instances=1,
            coalesce=True,
        )

        scheduler.add_job(
            fail_stalled_searches,
            trigger='interval',
            minutes=15,
            id='sweeper_stalled_searches',
            max_instances=1,
            coalesce=True,
        )
        
        

        scheduler.add_job(
            dispatch_preferences,
            trigger='cron',
            day_of_week=CRON_DAY_OF_WEEK,
            hour=CRON_HOUR,
            minute=CRON_MINUTE,
            id='process_preferences',
            max_instances=1,
            coalesce=True,
        )

        logger.info('Scheduler Django iniciado com sucesso.')
        scheduler.start()