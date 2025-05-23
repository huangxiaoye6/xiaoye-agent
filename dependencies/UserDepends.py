from utils.redis import get_redis
async def get_redis_depend():
    redis=await get_redis()
    return redis