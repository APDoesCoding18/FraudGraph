import json
import logging
from aiokafka import AIOKafkaProducer
from app.core.config import settings
from app.events.schemas import TransactionEvent

logger = logging.getLogger(__name__)

class KafkaProducer:
    def __init__(self):
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        await self.producer.start()
        logger.info("Kafka Producer started")

    async def stop(self):
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka Producer stopped")

    async def publish_transaction_event(self, event: TransactionEvent):
        if not self.producer:
            raise RuntimeError("Kafka Producer is not initialized")
        
        await self.producer.send_and_wait(
            topic=settings.KAFKA_TRANSACTION_TOPIC,
            key=str(event.transaction_id).encode("utf-8"),
            value=event.model_dump(mode="json")
        )
        logger.info(f"Published transaction event for {event.transaction_id}")

kafka_producer = KafkaProducer()
