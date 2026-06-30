import json
import os
import pika
import logging
import time
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from search.models import SearchRequest, Course, SavedAlert
from core.models import NotificationSent
from search.choices import SearchStatus
from search.emails import send_results_email, send_no_results_email
from core.emails import send_alerts_digest_email, send_new_courses_email

logger = logging.getLogger(__name__)
User = get_user_model()

class Command(BaseCommand):
    help = 'Consome os resultados processados pelo Worker e salva na base de dados'

    def handle(self, *args, **options):
        rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        results_queue = os.getenv("RABBITMQ_RESULTS_QUEUE", "search_results")
        
        connection = None
        while True:
            try:
                self.stdout.write(f"Tentando conectar ao RabbitMQ em {rabbitmq_host}...")
                connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
                break
            except pika.exceptions.AMQPConnectionError:
                self.stdout.write(self.style.WARNING("RabbitMQ ainda não está pronto. Tentando de novo em 5 segundos..."))
                time.sleep(5) 

        channel = connection.channel()
        channel.queue_declare(queue=results_queue, durable=True)
        channel.basic_qos(prefetch_count=1)

        def callback(ch, method, properties, body):
            try:
                payload = json.loads(body.decode("utf-8"))
                job_type = payload.get("job_type", "manual") 
                logger.info(f"Recebido resultado do Worker: job_id={payload.get('job_id')} tipo={job_type}")

                if job_type == "manual":
                    self._process_manual_search(payload)
                elif job_type in ["alert_requested", "preference_requested"]:
                    self._process_background_job(payload)

                ch.basic_ack(delivery_tag=method.delivery_tag)

            except json.JSONDecodeError:
                logger.error("Falha ao decodificar JSON da fila de resultados.")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.exception(f"Erro crítico no consumer_result: {str(e)}")
                ch.basic_ack(delivery_tag=method.delivery_tag)

        self.stdout.write(self.style.SUCCESS(f"Web Consumer iniciado. Aguardando na fila '{results_queue}'..."))
        channel.basic_consume(queue=results_queue, on_message_callback=callback, auto_ack=False)
        channel.start_consuming()

    def _process_manual_search(self, payload):
            """Lida com as buscas que o usuário clicou ativamente no site."""
            search_id = payload.get("job_id")
            status = payload.get("status")
            courses_data = payload.get("courses", [])
            email = payload.get("notification_email")
            keywords = payload.get("keywords", "")

            try:
                search_request = SearchRequest.objects.get(id=search_id)

                if status == "COMPLETED" and courses_data:
                    Course.objects.bulk_create([
                        Course(
                            search_request=search_request,
                            name=c["name"],
                            institution=c["institution"],
                            modality=c["modality"],
                            state=c["state"],
                            link=c.get("link", ""),
                        ) for c in courses_data
                    ])
                    search_request.results_count = len(courses_data)

                search_request.status = status
                search_request.save(update_fields=["status", "results_count", "updated_at"])

                if status == "COMPLETED":
                    send_results_email(user_email=email, courses=courses_data, search_id=search_request.id)         
                elif status == "NO_RESULTS":
                    send_no_results_email(user_email=email, search_id=search_request.id, keywords=keywords)
                
                logger.info(f"Busca manual {search_id} finalizada. Status: {status}")

            except SearchRequest.DoesNotExist:
                logger.error(f"SearchRequest {search_id} não encontrada na base de dados. Descartando.")
            except Exception as e:
                logger.error(f"Erro ao enviar e-mail para a busca manual {search_id}: {e}")
        
    def _process_background_job(self, payload):
        """Lida com os alertas e preferências disparados pelo run_scheduler."""
        email = payload.get("notification_email")
        courses_data = payload.get("courses", [])
        job_type = payload.get("job_type")
        job_id = payload.get("job_id")

        if not courses_data or payload.get("status") != "COMPLETED":
            return 
        
        try:
            user = User.objects.get(email=email)
            new_courses = []

            # Lógica de Deduplicação: Só queremos avisar o usuário sobre cursos INÉDITOS
            for c_data in courses_data:
                fingerprint = NotificationSent.fingerprint_for(c_data["name"], c_data["institution"])
                
                # Verifica se este usuário já foi notificado sobre este curso específico
                already_sent = NotificationSent.objects.filter(
                    user=user, 
                    course_fingerprint=fingerprint
                ).exists()

                if not already_sent:
                    new_courses.append(c_data)
                    # Registra que agora ele foi notificado para não enviar de novo semana que vem
                    NotificationSent.objects.create(
                        user=user,
                        course_fingerprint=fingerprint,
                        course_name=c_data["name"],
                        course_institution=c_data["institution"],
                        course_link=c_data.get("link", "")
                    )

            if new_courses:
                if job_type == "alert_requested":
                    try:
                        alert = SavedAlert.objects.get(id=job_id) 
                        sections = [{'alert_name': alert.name, 'courses': new_courses}]
                        send_alerts_digest_email(user_email=email, sections=sections)
                        logger.info(f"Alerta enviado: {len(new_courses)} novos cursos para {email}.")
                    except SavedAlert.DoesNotExist:
                        logger.error(f"SavedAlert com ID {job_id} não encontrado para montagem do digest.")
                elif job_type == "preference_requested":
                    send_new_courses_email(user_email=email, courses=new_courses)
                    logger.info(f"Preferências enviadas: {len(new_courses)} novos cursos para {email}.")
            else:
                logger.info(f"Background ({job_type}): Todos os {len(courses_data)} cursos já tinham sido notificados a {email}.")
             
        except User.DoesNotExist:
            logger.error(f"Usuário com email {email} não encontrado para notificação em background.")
        except Exception as e:
            logger.error(f"Falha inesperada no processamento de e-mails em background: {e}")
