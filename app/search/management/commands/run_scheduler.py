import os
import logging
from django.core.management.base import BaseCommand
from apscheduler.schedulers.blocking import BlockingScheduler
from search.tasks import dispatch_saved_alerts

logger = logging.getLogger('optio.scheduler')

class Command(BaseCommand):
    help = 'Inicia o orquestrador de jobs em background do Django'

    def handle(self, *args, **options):
        TIMEZONE = os.getenv('NOTIFY_TIMEZONE', 'America/Sao_Paulo')
        ALERTS_INTERVAL = int(os.getenv('ALERTS_INTERVAL_SECONDS', 604800))
        
        scheduler = BlockingScheduler(timezone=TIMEZONE)
        
        scheduler.add_job(
            dispatch_saved_alerts,
            trigger='interval',
            seconds=ALERTS_INTERVAL,
            id='process_saved_alerts',
            max_instances=1,
            coalesce=True,
        )
        
        logger.info('Scheduler Django iniciado com sucesso.')
        scheduler.start()