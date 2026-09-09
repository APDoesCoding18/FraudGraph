import json
import logging
import asyncio
from aiokafka import AIOKafkaConsumer
from app.core.config import settings
from app.events.schemas import TransactionEvent
from app.events.handlers import handle_transaction_event
from app.database.postgres import AsyncSessionLocal

logger = logging.getLogger(__name__)

class KafkaEventConsumer:
    def __init__(self):
        self.consumer = None
        self.task = None
        self._stop_event = asyncio.Event()

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            settings.KAFKA_TRANSACTION_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id="fraud-processing-group",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            enable_auto_commit=False, # We commit manually after successful processing
            auto_offset_reset="earliest"
        )
        await self.consumer.start()
        self._stop_event.clear()
        self.task = asyncio.create_task(self.consume_loop())
        logger.info("Kafka Consumer started")

    async def stop(self):
        if self.consumer:
            self._stop_event.set()
            if self.task:
                await self.task # Wait for current loop to finish
            await self.consumer.stop()
            logger.info("Kafka Consumer stopped")

    async def consume_loop(self):
        while not self._stop_event.is_set():
            try:
                # Use getmany to poll with a timeout so we can check _stop_event
                msg_pack = await self.consumer.getmany(timeout_ms=1000)
                for tp, messages in msg_pack.items():
                    for msg in messages:
                        await self.process_message(msg)
            except Exception as e:
                logger.error(f"Error in Kafka consumer loop: {e}")
                await asyncio.sleep(5) # Backoff on critical failure
                
    async def process_message(self, msg):
        try:
            event = TransactionEvent(**msg.value)
        except Exception as e:
            logger.error(f"Failed to deserialize message: {msg.value}, error: {e}")
            # Invalid schema, commit to avoid poison pill loop
            await self.consumer.commit()
            return
            
        MAX_RETRIES = 3
        for attempt in range(MAX_RETRIES):
            async with AsyncSessionLocal() as session:
                try:
                    await handle_transaction_event(event, session)
                    await self.consumer.commit()
                    return # Success
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for event {event.transaction_id}: {e}")
                    await asyncio.sleep(2 ** attempt) # Exponential backoff
        
        # Dead-letter path: After MAX_RETRIES exhaustion
        logger.error(f"Event {event.transaction_id} exhausted all retries. Routing to dead-letter path.")
        # In a real system, we'd publish to a DLQ topic here.
        # For now, we log the failure and commit so we don't block the partition indefinitely.
        await self.consumer.commit()

kafka_consumer = KafkaEventConsumer()
