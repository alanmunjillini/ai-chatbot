import redis
from app.core.config import REDIS_HOST, REDIS_PORT

#创建 Redis 连接
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)