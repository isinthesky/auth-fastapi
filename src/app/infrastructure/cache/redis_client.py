# src/app/infrastructure/cache/redis_client.py

from redis import Redis
from src.settings.environment import RedisEnvironment

redis_client = Redis(
    host=RedisEnvironment.REDIS_HOST,
    port=RedisEnvironment.REDIS_PORT,
    password=RedisEnvironment.REDIS_PASSWORD,
    db=0,
    decode_responses=True
)

class RedisCache:
    def __init__(self, client: Redis = redis_client):
        self.client = client

    async def get(self, key: str) -> str:
        return await self.client.get(key)

    async def set(self, key: str, value: str, expire: int = None):
        await self.client.set(key, value, ex=expire)

    async def delete(self, key: str):
        await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        return await self.client.exists(key)