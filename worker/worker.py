import os
import time  
import pika

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

while True:
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        break
    except pika.exceptions.AMQPConnectionError:
        print("RabbitMQ não disponível, tentando novamente em 5s...", flush=True)
        time.sleep(5)

channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

def callback(ch, method, properties, body):
    print(f"[X] Received {body.decode()}", flush=True)

channel.basic_consume(
    queue='task_queue',
    on_message_callback=callback,
    auto_ack=True
)

print ("[*] Esperando por mensagens...", flush=True)
channel.start_consuming()