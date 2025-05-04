from redis.asyncio import Redis

from app.models.user import UserCreate, UserInDB
from app.utils.security import get_password_hash


async def get_user_by_username(db: Redis, username: str) -> UserInDB | None:
    """Fetches a user from Redis by username."""
    user_data = await db.hgetall(f"user:{username}")
    if not user_data:
        return None
    # Ensure id is set correctly, using username as the key identifier
    return UserInDB(id=username, **user_data)


async def create_user(db: Redis, user: UserCreate) -> UserInDB:
    """Creates a new user in Redis."""
    hashed_password = get_password_hash(user.password)
    user_data = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
    }
    # Use hmset (or hset in newer redis-py versions) to store the hash
    await db.hmset(f"user:{user.username}", user_data)
    # Return the created user data, ensuring id is set
    return UserInDB(id=user.username, **user_data)
