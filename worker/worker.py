import json
import os
import time
import sys

import pika

sys.path.append("/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "optio.settings")

import django
django.setup()
from search.emails import EmailDeliveryError, send_results_email

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUE_NAME = os.getenv("RABBITMQ_QUEUE", "search_requests")


def connect_to_rabbitmq():
    while True:
        try:
            print(f"Tentando conectar ao RabbitMQ em {RABBITMQ_HOST}...", flush=True)

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )

            print("Conectado ao RabbitMQ!", flush=True)
            return connection

        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ não disponível, tentando novamente em 5s...", flush=True)
            time.sleep(5)


def process_search_request(payload: dict) -> None:
    search_id = payload.get("search_request_id")
    user_email = payload.get("notification_email")
    
    print("=" * 60, flush=True)
    print("Nova solicitação de busca recebida", flush=True)
    print(f"ID da busca: {payload.get('search_request_id')}", flush=True)
    print(f"E-mail de notificação: {payload.get('notification_email')}", flush=True)
    print(f"Palavras-chave: {payload.get('keywords')}", flush=True)
    print(f"Área: {payload.get('area')}", flush=True)
    print(f"Modalidade: {payload.get('modality')}", flush=True)
    print(f"Estado: {payload.get('state')}", flush=True)
    print("=" * 60, flush=True)
    
    courses = [
        {
            "title": "Pós-graduação em Engenharia de Software",
            "institution": "Instituição Exemplo",
            "modality": "EAD",
            "state": "PB",
            "url": "https://exemplo.com/curso-engenharia-software",
        },
        {
            "title": "Especialização em Ciência de Dados",
            "institution": "Universidade Exemplo",
            "modality": "Presencial",
            "state": "SP",
            "url": "https://exemplo.com/curso-ciencia-dados",
        },
    ]
    
    try:
        send_results_email(
            user_email=user_email,
            courses=courses,
            search_id=search_id,
        )

        print(
            f"E-mail de resultados enviado para a busca {search_id}.",
            flush=True,
        )

    except EmailDeliveryError as error:
        print(
            f"Falha ao enviar e-mail da busca {search_id}: {error}",
            flush=True,
        )

    # Próximas etapas futuras:
    # 1. buscar dados em fontes externas
    # 2. processar resposta com LLM
    # 3. salvar resultados no banco
    # 4. atualizar status da SearchRequest
    # 5. notificar o usuário


def callback(ch, method, properties, body):
    try:
        payload = json.loads(body.decode())

        if payload.get("type") != "search_requested":
            print(
                f"Mensagem ignorada. Tipo desconhecido: {payload.get('type')}",
                flush=True,
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        process_search_request(payload)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError:
        print("Mensagem inválida: payload não é JSON.", flush=True)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as error:
        print(f"Erro ao processar mensagem: {error}", flush=True)
        ch.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=True,
        )


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

print(f"[*] Worker aguardando mensagens na fila '{QUEUE_NAME}'...", flush=True)

channel.start_consuming()