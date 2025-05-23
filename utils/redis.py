import aioredis
redis:aioredis.Redis=None
import os
redis_cache_url=os.getenv('REDIS_CACHE_URL')
async def connection_redis():
    global redis
    pool=aioredis.ConnectionPool.from_url(redis_cache_url,encoding="utf-8", decode_responses=True)
    redis=await aioredis.Redis(connection_pool=pool)


async def close_redis():
    await redis.close()

def get_redis():
    return redis