import json
import os
import time
import sys
import logging
import traceback
import pika

sys.path.append("/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "optio.settings")

import django
django.setup()
from search.emails import EmailDeliveryError, send_results_email
from search.choices import SearchStatus 
from search.models import SearchRequest

logging.basicConfig(
    level = os.getenv("WORKER_LOG_LEVEL", "INFO"),
    format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("optio.worker")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUE_NAME = os.getenv("RABBITMQ_QUEUE", "search_requests")

class InvalidMessageError(Exception):
    pass

def connect_to_rabbitmq():
    while True:
        try:
            logger.info(f"Tentando conectar ao RabbitMQ em {RABBITMQ_HOST}...")

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )

            logger.info("Conectado ao RabbitMQ!")
            return connection

        except pika.exceptions.AMQPConnectionError:
            logger.error("RabbitMQ não disponível, tentando novamente em 5s...")
            time.sleep(5)


def validate_payload(payload: dict) -> None:
    required_fields = [
        "type",
        "search_request_id",
        "user_id",
        "notification_email",
        "keywords",
    ]
    
    missing_fields = [
        field for field in required_fields if not payload.get(field)
    ] 
    
    if missing_fields:
        raise InvalidMessageError(f"Payload inválido: campos obrigatórios ausentes: {', '.join(missing_fields)}")
    
    if payload.get("type") != "search_requested":
        raise InvalidMessageError(f"Tipo de mensagem desconhecido: {payload.get('type')}")
    
    
    
    
def get_mock_courses(payload: dict) -> list[dict]:
    keywords = payload.get("keywords", "curso")
    return [
        {
            "title": f"Pós-graduação em {keywords.title()}",
            "institution": "Instituição Exemplo",
            "modality": payload.get("modality") or "EAD",
            "state": payload.get("state") or "PB",
            "url": "https://exemplo.com/curso-pos-graduacao",
        },
        {
            "title": "Especialização em Ciência de Dados",
            "institution": "Universidade Exemplo",
            "modality": "Presencial",
            "state": "SP",
            "url": "https://exemplo.com/especializacao-ciencia-dados",
        },
    ]
    
def mark_search_status(search_id: int, status: str, results_count: int | None = None) -> None:
    update_fields = ["status"]
    
    search_request = SearchRequest.objects.filter(id=search_id).first()
    search_request.status = status
    
    if results_count is not None:
        search_request.results_count = results_count
        update_fields.append("results_count")
        
    search_request.save(update_fields=update_fields)


def process_search_request(payload: dict) -> None:
    validate_payload(payload)
    
    search_id = payload["search_request_id"]
    user_email = payload["notification_email"]
    
    logger.info("Nova solicitação de busca recebida")
    logger.info(f"ID da busca: {payload.get('search_request_id')}")
    logger.info(f"E-mail de notificação: {payload.get('notification_email')}")
    logger.info(f"Palavras-chave: {payload.get('keywords')}")
    logger.info(f"Área: {payload.get('area')}")
    logger.info(f"Modalidade: {payload.get('modality')}")
    logger.info(f"Estado: {payload.get('state')}")
    logger.info("=" * 60)
    
    mark_search_status(search_id, SearchStatus.PROCESSING)
    courses = get_mock_courses(payload)

    send_results_email(
        user_email=user_email,
        courses=courses,
        search_id=search_id,
    )

    logger.info(
    "Solicitação processada com sucesso. search_id=%s results_count=%s",
    search_id,
    len(courses),
)

    # Próximas etapas futuras:
    # 1. buscar dados em fontes externas
    # 2. processar resposta com LLM
    # 3. salvar resultados no banco
    # 4. atualizar status da SearchRequest
    # 5. notificar o usuário


def callback(ch, method, properties, body):
    delivery_tag = method.delivery_tag
    logger.info("Mensagem recebida do RabbitMQ. delivery_tag=%s", delivery_tag)
    
    try:
        payload = json.loads(body.decode("utf-8"))
        logger.debug(f"Payload recebido: {payload}")

        process_search_request(payload)

        ch.basic_ack(delivery_tag=method.delivery_tag)
        
        logger.info(
            "Mensagem confirmada com ACK. delivery_tag=%s",
            delivery_tag,
        )

    except json.JSONDecodeError:
        logger.exception(
            "Mensagem descartada: corpo não é JSON válido. delivery_tag=%s body=%r",
            delivery_tag,
            body,
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as error:
        logger.exception(f"Erro ao processar mensagem: {error}")
        ch.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=True,
        )
        
    except InvalidMessageError as error:
        logger.error(
            "Mensagem inválida descartada. delivery_tag=%s error=%s body=%r",
            delivery_tag,
            error,
            body,
        )

        # Erro permanente: payload ruim.
        ch.basic_ack(delivery_tag=delivery_tag)

    except SearchRequest.DoesNotExist:
        logger.exception(
            "SearchRequest não encontrada. Mensagem descartada. delivery_tag=%s body=%r",
            delivery_tag,
            body,
        )

        # Erro permanente: não existe busca no banco.
        ch.basic_ack(delivery_tag=delivery_tag)

    except EmailDeliveryError as error:
        logger.exception(
            "Falha no envio de e-mail. Mensagem não será reprocessada automaticamente. delivery_tag=%s error=%s",
            delivery_tag,
            error,
        )
        
        try:
            payload = json.loads(body.decode("utf-8"))
            search_id = payload.get("search_request_id")

            if search_id:
                mark_search_status(search_id, SearchStatus.FAILED)

        except Exception:
            logger.exception(
                "Falha adicional ao marcar SearchRequest como FAILED."
            )
            
            
        # Importante: ACK para não gerar loop infinito.
        # Futuramente podemos usar Dead Letter Queue.
        ch.basic_ack(delivery_tag=delivery_tag)
    
    except Exception as error:
        logger.exception(
            "Erro inesperado ao processar mensagem. delivery_tag=%s error=%s body=%r",
            delivery_tag,
            error,
            traceback.format_exc(),
        )
        # Para este momento do projeto, evitamos loop infinito.
        # Futuramente: enviar para DLQ ou controlar tentativas.
        ch.basic_ack(delivery_tag=delivery_tag)

connection = connect_to_rabbitmq()
channel = connection.channel()

channel.queue_declare(
    queue=QUEUE_NAME,
    durable=True,
)

channel.basic_qos(prefetch_count=1)

channel.basic_consume(
    queue=QUEUE_NAME,
    on_message_callback=callback,
    auto_ack=False,
)

logger.info(
    "Worker aguardando mensagens. queue=%s",
    QUEUE_NAME,
)

channel.start_consuming()