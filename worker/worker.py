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
from providers.finder import CourseFinder
from domain.use_cases import SearchProcessor

def main():
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
    QUEUE_NAME = os.getenv("RABBITMQ_QUEUE", "search_requests")

    processor = SearchProcessor(
        repository=SearchRepository(),
        notifier=EmailNotificationService(),
        finder=CourseFinder(),
    )

    consumer = RabbitMQConsumer(host=RABBITMQ_HOST, queue=QUEUE_NAME, processor=processor)
    logger.info("Worker inicializado. Aguardando mensagens.")
    consumer.start()

if __name__ == "__main__":
    main()