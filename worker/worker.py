import json
import os
import time

import pika


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
    print("=" * 60, flush=True)
    print("Nova solicitação de busca recebida", flush=True)
    print(f"ID da busca: {payload.get('search_request_id')}", flush=True)
    print(f"ID do usuário: {payload.get('user_id')}", flush=True)
    print(f"E-mail de notificação: {payload.get('notification_email')}", flush=True)
    print(f"Palavras-chave: {payload.get('keywords')}", flush=True)
    print(f"Área: {payload.get('area')}", flush=True)
    print(f"Modalidade: {payload.get('modality')}", flush=True)
    print(f"Estado: {payload.get('state')}", flush=True)
    print("=" * 60, flush=True)

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