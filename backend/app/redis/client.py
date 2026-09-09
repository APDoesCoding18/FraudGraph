import redis.asyncio as redis
from app.core.config import settings

class RedisClient:
    def __init__(self):
        self.pool = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def close(self):
        await self.pool.close()

redis_client = RedisClient()

async def get_redis():
    return redis_client.pool
