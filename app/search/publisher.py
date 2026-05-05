#Isola a lógica de comunicação com o RabbitMQ em um módulo separado, facilitando a manutenção e a reutilização do código.

import json
import os

import pika


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "search_requests")


class QueuePublishError(Exception): # implementar quando tiver tempo tempo 
    pass


def publish_search_request(search_request) -> None:
    payload = {
        "type": "search_requested",
        "search_request_id": search_request.id,
        "user_id": search_request.user_id,
        "keywords": search_request.keywords,
        "area": search_request.area,
        "modality": search_request.modality,
        "state": search_request.state,
        "created_at": search_request.created_at.isoformat(),
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