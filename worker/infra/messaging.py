import json
import time
import logging
import pika

from domain.exceptions import InvalidMessageError, SearchNotFoundError
from domain.contracts import SearchRequestedEvent

from search.emails import EmailDeliveryError
from search.choices import SearchStatus

logger = logging.getLogger("optio.worker.messaging")

class RabbitMQConsumer:
    def __init__(self, host: str, queue: str, processor):
        self.host = host
        self.queue = queue
        self.processor = processor

    def connect(self):

        while True:
            try:
                logger.info("Tentando conectar ao RabbitMQ em %s...", self.host)
                return pika.BlockingConnection(pika.ConnectionParameters(host=self.host, ))
            except pika.exceptions.AMQPConnectionError:
                logger.error("RabbitMQ não disponível, tentando novamente em 5s...")
                time.sleep(5)

    def start(self):
        connection = self.connect()
        channel = connection.channel()
        channel.queue_declare(queue=self.queue, durable=True)
        channel.basic_qos(prefetch_count=1)

        def callback(ch, method, properties, body):
            delivery_tag = method.delivery_tag
            payload = None

            try:
                payload = json.loads(body.decode("utf-8"))
                event = SearchRequestedEvent.from_payload(payload)
                self.processor.process(event)
                ch.basic_ack(delivery_tag=delivery_tag)


            except json.JSONDecodeError:
                logger.exception("Corpo da mensagem não é JSON válido.")
                ch.basic_ack(delivery_tag=delivery_tag)
            except InvalidMessageError as error:
                logger.error("Payload inválido — descartado. error=%s", error)
                ch.basic_ack(delivery_tag=delivery_tag)
            except SearchNotFoundError:
                logger.exception("SearchRequest não encontrada — descartada.")
                ch.basic_ack(delivery_tag=delivery_tag)
            except EmailDeliveryError as error:
                logger.exception("Falha no envio de e-mail. error=%s", error)
                ch.basic_ack(delivery_tag=delivery_tag)
            except Exception as error:
                logger.exception("Erro inesperado. error=%s", error)
                if payload and payload.get("search_request_id"):
                    try:
                        self.processor.repository.mark_search_status(payload.get("search_request_id"), SearchStatus.FAILED.value)
                    except Exception:
                        pass
                ch.basic_ack(delivery_tag=delivery_tag)

        logger.info("Worker aguardando mensagens. queue=%s", self.queue)
        channel.basic_consume(queue=self.queue, on_message_callback=callback, auto_ack=False)
        channel.start_consuming()

class RabbitMQPublisher:
    def __init__(self, host: str, queue: str):
        self.host = host
        self.queue = queue

    def publish_results(self, search_id: int, status: str, courses: list = None, keywords: str = None):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
        channel = connection.channel()
        channel.queue_declare(queue=self.queue, durable=True)

        payload = {
            "search_request_id": search_id,
            "status": status,
            "keywords": keywords,
            "notification_email": email,
            "courses": [
                {
                    "name": c.name, 
                    "institution": c.institution, 
                    "modality": c.modality, 
                    "state": c.state, 
                    "link": c.link
                } for c in (courses or [])
            ]
        }

        channel.basic_publish(
            exchange="",
            routing_key=self.queue,
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        logger.info(f"Resultado publicado para search_id={search_id} na fila {self.queue}")
