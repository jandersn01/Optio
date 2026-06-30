# app/search/tasks.py
from datetime import timedelta
from django.utils import timezone
import logging
from search.choices import SearchStatus
from search.models import SavedAlert, SearchRequest
from core.models import NotificationPreference
from search.publisher import publish_background_job

logger = logging.getLogger(__name__)

def dispatch_preferences():
    """Busca preferências ativas e publica na fila para o worker."""
    prefs = NotificationPreference.objects.filter(active=True).select_related("user")
    
    dispatched = 0
    for pref in prefs:
        if not pref.area_list:
            continue # Ignora se o usuário não definiu áreas
            
        for area in pref.area_list:
            criteria = {
                "keywords": area, # Usa a área como keyword para a busca
                "area": area,
                "modality": pref.modality,
                "state": "", # Se não houver estado preferido global
            }
            try:
                publish_background_job(
                    job_type="preference_requested",
                    job_id=pref.user.id, # O ID do job pode ser o do usuário
                    notification_email=pref.user.email,
                    criteria=criteria
                )
                dispatched += 1
            except Exception as e:
                logger.error(f"Erro ao despachar preferência do usuário {pref.user.id}: {e}")
                
    logger.info(f"Scheduler: {dispatched} preferências enviadas para a fila.")

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

def fail_stalled_searches():
    """Varre requisições que estão presas no estado PROCESSING há muito tempo e marca-as como falhadas."""
    # Define o tempo máximo tolerável (ex: 5 minutos atrás)
    timeout_threshold = timezone.now() - timedelta(minutes=5)

    stalled_searches = SearchRequest.objects.filter(
        status__in=[SearchStatus.PENDING, SearchStatus.PROCESSING],
        created_at__lt=timeout_threshold
    )

    count = stalled_searches.update(status=SearchStatus.FAILED)
    if count > 0:
        logger.warning(f"Sweeper do Django: {count} buscas travadas foram marcadas como FAILED devido a timeout.")