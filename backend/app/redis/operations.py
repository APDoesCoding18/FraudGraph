from uuid import UUID
import time
from app.events.schemas import TransactionEvent
from app.redis.client import redis_client

class RedisOperations:
    def __init__(self, client):
        self.client = client

    async def _zcount_window(self, key: str, window_seconds: int) -> int:
        now = time.time()
        min_score = now - window_seconds
        
        # We can clean up here optionally, but pipelined writes will do the cleanup.
        # Just return the count
        return await self.client.zcount(key, min_score, now)

    async def count_transactions(self, account_id: UUID, window_seconds: int) -> int:
        key = f"tx_history:{account_id}"
        return await self._zcount_window(key, window_seconds)

    async def has_incoming_funds(self, account_id: UUID, window_seconds: int) -> bool:
        key = f"incoming:{account_id}"
        count = await self._zcount_window(key, window_seconds)
        return count > 0

    async def count_outgoing_transactions(self, account_id: UUID, window_seconds: int) -> int:
        key = f"outgoing_tx:{account_id}"
        return await self._zcount_window(key, window_seconds)

    async def count_distinct_counterparties(self, account_id: UUID, window_seconds: int) -> int:
        key = f"counterparties:{account_id}"
        return await self._zcount_window(key, window_seconds)

    async def count_distinct_incoming(self, account_id: UUID, window_seconds: int) -> int:
        key = f"incoming:{account_id}"
        return await self._zcount_window(key, window_seconds)

    async def count_distinct_outgoing(self, account_id: UUID, window_seconds: int) -> int:
        key = f"outgoing:{account_id}"
        return await self._zcount_window(key, window_seconds)

    async def record_transaction(self, event: TransactionEvent) -> None:
        """
        Record transaction details into ZSETs for sliding window analysis.
        Strict 1-hour TTL enforced on all keys.
        """
        now = time.time()
        ttl = 3600 # 1 hour
        min_score = now - ttl
        
        pipeline = self.client.pipeline()

        sender = str(event.sender_account_id)
        receiver = str(event.receiver_account_id)
        tx_id = str(event.transaction_id)
        
        keys_to_update = [
            (f"tx_history:{sender}", tx_id),
            (f"outgoing_tx:{sender}", tx_id),
            (f"outgoing:{sender}", receiver), # distinct outgoing counterparty
            (f"counterparties:{sender}", receiver),
            
            (f"tx_history:{receiver}", tx_id),
            (f"incoming:{receiver}", sender), # distinct incoming counterparty
            (f"counterparties:{receiver}", sender)
        ]

        for key, member in keys_to_update:
            # Add to ZSET
            pipeline.zadd(key, {member: now})
            # Remove elements older than 1 hour to keep ZSET small
            pipeline.zremrangebyscore(key, "-inf", min_score)
            # Enforce strict 1 hour TTL on the key itself
            pipeline.expire(key, ttl)

        await pipeline.execute()

# Singleton instance
redis_ops = RedisOperations(redis_client.pool)
