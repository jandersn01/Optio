import json
import time
import logging
import pika
import functools
from concurrent.futures import ThreadPoolExecutor

from domain.exceptions import InvalidMessageError
from domain.contracts import JobRequest

logger = logging.getLogger("optio.worker.messaging")

class RabbitMQConsumer:
    def __init__(self, host: str, queue: str, processor, max_workers : int = 5):
        self.host = host
        self.queue = queue
        self.processor = processor
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

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
        
        channel.basic_qos(prefetch_count=self.max_workers)
        
        def ack_message(ch, delivery_tag):
            if ch.is_open:
                ch.basic_ack(delivery_tag)
                logger.debug(f"Message {delivery_tag} ACKed na Main Thread.")


        def process_message_thread(connection, ch, delivery_tag, payload):
            """Esta função roda nas threads do pool"""
            try:
                request = JobRequest.from_payload(payload)
                self.processor.process(request)
                
                # Agenda o ACK de forma segura na thread principal
                cb = functools.partial(ack_message, ch, delivery_tag)
                connection.add_callback_threadsafe(cb)
            except InvalidMessageError as error:
                logger.error("Payload inválido — descartado. error=%s", error)
                cb = functools.partial(ack_message, ch, delivery_tag)
                connection.add_callback_threadsafe(cb)
            except Exception as error:
                logger.exception("Erro ao processar mensagem. error=%s", error)
                job_id = payload.get("job_id")
                job_type = payload.get("job_type", "manual")
                email = payload.get("notification_email", "")
                if job_id:
                    try:
                        self.processor.publisher.publish_result(
                            job_id=job_id,
                            job_type=job_type,
                            status="FAILED",
                            email=email,
                            criteria=payload.get("criteria", {})
                        )
                        logger.info("Aviso de FAILED enviado ao Django para job_id=%s", job_id)
                    except Exception as pub_error:
                        logger.error("Falha catastrófica ao tentar notificar o Django: %s", pub_error)
                
                # Acknowledge mesmo em erro para não travar a fila em loop infinito
                cb = functools.partial(ack_message, ch, delivery_tag)
                connection.add_callback_threadsafe(cb)

        def callback(ch, method, properties, body):
            delivery_tag = method.delivery_tag
            try:
                payload = json.loads(body.decode("utf-8"))
                self.executor.submit(process_message_thread, connection, ch, delivery_tag, payload)
            except json.JSONDecodeError:
                logger.exception("Corpo da mensagem não é JSON válido. Impossível recuperar job_id.")
                ch.basic_ack(delivery_tag=delivery_tag)

        logger.info("Worker aguardando mensagens com ThreadPool(workers=%d). queue=%s", self.max_workers, self.queue)
        channel.basic_consume(queue=self.queue, on_message_callback=callback, auto_ack=False)
        try:

            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
            self.executor.shutdown(wait=True)
            connection.close()

class RabbitMQPublisher:
    def __init__(self, host: str, queue: str):
        self.host = host
        self.queue = queue

    def publish_result(self, job_id: str, job_type: str, status: str, email: str, criteria: dict, courses: list = None): 
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
        channel = connection.channel()
        channel.queue_declare(queue=self.queue, durable=True)

        payload = {
            "job_id": job_id,
            "job_type": job_type,
            "status": status,
            "notification_email": email,
            "criteria": criteria,
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
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="aplication/json"
                )
        )
        connection.close()
        logger.info(f"Resultado publicado para search_id={job_id} na fila {self.queue}")
