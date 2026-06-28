import os
import logging 

logging.basicConfig(
    level=os.getenv("WORKER_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("worker.worker.main")

from infra.repositories import SearchRepository
from infra.notifications import EmailNotificationService

from infra.messaging import RabbitMQConsumer
from domain.use_cases import SearchProcessor

def main():
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
    QUEUE_NAME = os.getenv("RABBITMQ_QUEUE", "search_requests")

    repository = SearchRepository()
    notifier = EmailNotificationService()

    processor = SearchProcessor(repository=repository, notifier=notifier)

    consumer = RabbitMQConsumer(host=RABBITMQ_HOST, queue=QUEUE_NAME, processor=processor)
    consumer.start()

    logger.info("Worker inicializado com sucesso.")

if __name__ == "__main__":
    main()