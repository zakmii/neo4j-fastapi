import redis.asyncio as redis

from app.utils.environment import CONFIG


async def get_redis_connection():
    """Creates and returns an asynchronous Redis connection pool."""
    try:
        # Use decode_responses=True to automatically decode responses from bytes to strings
        pool = redis.ConnectionPool.from_url(
            f"redis://{CONFIG.REDIS.HOST}:{CONFIG.REDIS.PORT}/{CONFIG.REDIS.DB}",
            username=CONFIG.REDIS.USERNAME,
            password=CONFIG.REDIS.PASSWORD,
            decode_responses=True,
        )
        connection = redis.Redis.from_pool(pool)
        await connection.ping()  # Verify connection
        print("Successfully connected to Redis")
        return connection
    except Exception as e:
        print(f"Error connecting to Redis: {e}")
        raise
