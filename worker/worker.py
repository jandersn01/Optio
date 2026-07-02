import os
import logging 

logging.basicConfig(
    level=os.getenv("WORKER_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("worker.main")

from infra.messaging import RabbitMQConsumer, RabbitMQPublisher
from providers.finder import CourseFinder
from domain.use_cases import SearchProcessor

def main():
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
    QUEUE_REQUESTS = os.getenv("RABBITMQ_QUEUE", "search_requests")
    QUEUE_RESULTS = os.getenv("RABBITMQ_RESULTS_QUEUE", "search_results")

    publisher = RabbitMQPublisher(
        host=RABBITMQ_HOST, 
        queue=QUEUE_RESULTS
    )
    finder = CourseFinder()
    processor = SearchProcessor(
        publisher=publisher,
        finder=finder,
    )

    consumer = RabbitMQConsumer(
        host=RABBITMQ_HOST,
        queue=QUEUE_REQUESTS,
        processor=processor)
    
    logger.info("Worker inicializado. Aguardando mensagens.")
    consumer.start()

if __name__ == "__main__":
    main()