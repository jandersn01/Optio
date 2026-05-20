import json
import os
import time
import sys
import logging

sys.path.append("/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "optio.settings")

import django
django.setup()

import pika
from search.emails import EmailDeliveryError, send_results_email, send_no_results_email
from search.choices import SearchStatus
from search.models import Course, SearchRequest
from scraper import search_courses_web
from prompts import build_prompt
from llm import call_llm, parse_llm_response

logging.basicConfig(
    level=os.getenv("WORKER_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("optio.worker")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUE_NAME = os.getenv("RABBITMQ_QUEUE", "search_requests")


class InvalidMessageError(Exception):
    pass


def connect_to_rabbitmq():
    while True:
        try:
            logger.info("Tentando conectar ao RabbitMQ em %s...", RABBITMQ_HOST)
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )
            logger.info("Conectado ao RabbitMQ!")
            return connection
        except pika.exceptions.AMQPConnectionError:
            logger.error("RabbitMQ não disponível, tentando novamente em 5s...")
            time.sleep(5)


def validate_payload(payload: dict) -> None:
    required_fields = ["type", "search_request_id", "user_id", "notification_email", "keywords"]
    missing = [f for f in required_fields if not payload.get(f)]
    if missing:
        raise InvalidMessageError(f"Campos obrigatórios ausentes: {', '.join(missing)}")
    if payload.get("type") != "search_requested":
        raise InvalidMessageError(f"Tipo de mensagem desconhecido: {payload.get('type')}")


def mark_search_status(search_id: int, status: str, results_count: int | None = None) -> None:
    search_request = SearchRequest.objects.filter(id=search_id).first()
    if not search_request:
        raise SearchRequest.DoesNotExist(f"SearchRequest {search_id} não encontrada.")

    update_fields = ["status"]
    search_request.status = status

    if results_count is not None:
        search_request.results_count = results_count
        update_fields.append("results_count")

    search_request.save(update_fields=update_fields)


def process_search_request(payload: dict) -> None:
    validate_payload(payload)

    search_id = payload["search_request_id"]
    user_email = payload["notification_email"]

    logger.info(
        "Nova solicitação de busca. search_id=%s keywords=%r area=%r modality=%r state=%r",
        search_id,
        payload.get("keywords"),
        payload.get("area"),
        payload.get("modality"),
        payload.get("state"),
    )

    mark_search_status(search_id, SearchStatus.PROCESSING)

    raw_content = search_courses_web(payload)
    prompt = build_prompt(payload, raw_content)
    llm_response = call_llm(prompt)
    courses_data = parse_llm_response(llm_response)

    # Tratamento de lista vazia (TASK 1)
    if not courses_data:
        mark_search_status(search_id, SearchStatus.NO_RESULTS, results_count=0)
        send_no_results_email(
            user_email=user_email,
            search_id=search_id,
            keywords=payload.get("keywords", ""),
        )
        logger.info(
            "Busca concluída sem resultados. search_id=%s",
            search_id,
        )
        return

    # Fluxo normal: cursos encontrados
    search_request = SearchRequest.objects.get(id=search_id)
    course_objects = [
        Course(
            search_request=search_request,
            name=c["name"],
            institution=c["institution"],
            modality=c["modality"],
            state=c["state"],
            link=c["link"],
        )
        for c in courses_data
    ]
    Course.objects.bulk_create(course_objects)

    mark_search_status(search_id, SearchStatus.COMPLETED, results_count=len(course_objects))

    send_results_email(
        user_email=user_email,
        courses=courses_data,
        search_id=search_id,
    )

    logger.info(
        "Busca concluída com sucesso. search_id=%s results=%d",
        search_id,
        len(course_objects),
    )


def callback(ch, method, properties, body):
    delivery_tag = method.delivery_tag
    logger.info("Mensagem recebida do RabbitMQ. delivery_tag=%s", delivery_tag)

    payload = None

    try:
        payload = json.loads(body.decode("utf-8"))
        logger.debug("Payload: %s", payload)
        process_search_request(payload)
        ch.basic_ack(delivery_tag=delivery_tag)
        logger.info("ACK enviado. delivery_tag=%s", delivery_tag)

    except json.JSONDecodeError:
        logger.exception(
            "Corpo da mensagem não é JSON válido. delivery_tag=%s body=%r",
            delivery_tag,
            body,
        )
        ch.basic_ack(delivery_tag=delivery_tag)

    except InvalidMessageError as error:
        logger.error(
            "Payload inválido — mensagem descartada. delivery_tag=%s error=%s",
            delivery_tag,
            error,
        )
        ch.basic_ack(delivery_tag=delivery_tag)

    except SearchRequest.DoesNotExist:
        logger.exception(
            "SearchRequest não encontrada — mensagem descartada. delivery_tag=%s",
            delivery_tag,
        )
        ch.basic_ack(delivery_tag=delivery_tag)

    except EmailDeliveryError as error:
        logger.exception(
            "Falha no envio de e-mail. delivery_tag=%s error=%s",
            delivery_tag,
            error,
        )
        # Cursos já foram salvos; não reprocessar para evitar duplicatas.
        ch.basic_ack(delivery_tag=delivery_tag)

    except Exception as error:
        logger.exception(
            "Erro inesperado ao processar mensagem. delivery_tag=%s error=%s",
            delivery_tag,
            error,
        )
        if payload:
            search_id = payload.get("search_request_id")
            if search_id:
                try:
                    mark_search_status(search_id, SearchStatus.FAILED)
                except Exception:
                    logger.exception("Falha ao marcar SearchRequest %s como FAILED.", search_id)
        ch.basic_ack(delivery_tag=delivery_tag)


connection = connect_to_rabbitmq()
channel = connection.channel()

channel.queue_declare(queue=QUEUE_NAME, durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=False)

logger.info("Worker aguardando mensagens. queue=%s", QUEUE_NAME)
channel.start_consuming()