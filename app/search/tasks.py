# app/search/tasks.py
import logging
from search.models import SavedAlert
from core.models import NotificationPreference
from search.publisher import publish_background_job

logger = logging.getLogger(__name__)

def dispatch_saved_alerts():
    """Busca alertas ativos e publica na fila do RabbitMQ para o worker processar."""
    alerts = SavedAlert.objects.filter(active=True).select_related("user")
    
    dispatched = 0
    for alert in alerts:
        criteria = {
            "keywords": alert.keywords,
            "area": alert.area,
            "modality": alert.modality,
            "state": alert.state,
        }
        try:
            publish_background_job(
                job_type="alert_requested",
                job_id=alert.id,
                notification_email=alert.user.email,
                criteria=criteria
            )
            dispatched += 1
        except Exception as e:
            logger.error(f"Erro ao despachar alerta {alert.id}: {e}")
            
    logger.info(f"Scheduler: {dispatched} alertas enviados para a fila.")
