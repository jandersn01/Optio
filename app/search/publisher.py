#Isola a lógica de comunicação com o RabbitMQ em um módulo separado, facilitando a manutenção e a reutilização do código.

import json
import os

import pika


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "search_requests")


class QueuePublishError(Exception): # implementar quando tiver tempo tempo 
    pass

def get_notification_email(search_request) -> str:
    if search_request.notification_email:
        return search_request.notification_email

    if search_request.user_id and search_request.user.email:
        return search_request.user.email

    raise QueuePublishError(
        f"SearchRequest {search_request.id} não possui e-mail de notificação."
    )

def publish_search_request(search_request) -> None:
    payload = {
        "job_id": str(search_request.id),
        "job_type": "manual",
        "notification_email": get_notification_email(search_request),
        "criteria": {
            "keywords": search_request.keywords,
            "area": search_request.area,
            "modality": search_request.modality,
            "state": search_request.state,
        }
    }

    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )

        channel = connection.channel()

        channel.queue_declare(
            queue=RABBITMQ_QUEUE,
            durable=True,
        )

        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_QUEUE,
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
            ),
        )

        connection.close()

    except pika.exceptions.AMQPError as error:
        raise QueuePublishError(
            f"Erro ao publicar SearchRequest {search_request.id} na fila."
        ) from error
    
def publish_background_job(job_type: str, job_id: int, notification_email: str, criteria: dict) -> None:
    """
    Publica um job gerado pelo Scheduler (alertas ou preferências) na fila.
    """
    payload = {
        "job_id": str(job_id),
        "job_type": job_type,  # Ex: "alert_requested" ou "preference_requested"
        "notification_email": notification_email,
        "criteria": {
            "keywords": criteria.get("keywords", ""),
            "area": criteria.get("area", ""),
            "modality": criteria.get("modality", ""),
            "state": criteria.get("state", ""),
        }
    }

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_QUEUE,
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
        )
        connection.close()
    except pika.exceptions.AMQPError as error:
        raise QueuePublishError(f"Erro ao publicar job {job_type} ID {job_id}.") from error