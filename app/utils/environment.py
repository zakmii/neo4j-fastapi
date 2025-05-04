# Packages and functions for loading environment variables
from typing import Optional

from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings

# Load environment from disk first, then apply any defaults
load_dotenv(find_dotenv(".env"))


class UvicornConfig(BaseSettings):
    PORT: int = 1026
    HOST: str = "0.0.0.0"

    WORKERS: int = 4
    RELOAD_ON_CHANGE: bool = False

    class Config:
        env_prefix = "UVICORN_"


class Neo4jConfig(BaseSettings):
    URI: str = "bolt://localhost:7687"
    USERNAME: str
    PASSWORD: str

    class Config:
        env_prefix = "NEO4J_"


class RedisConfig(BaseSettings):
    HOST: str = "localhost"
    PORT: int = 6379
    DB: int = 0

    USERNAME: Optional[str] = None
    PASSWORD: Optional[str] = None

    class Config:
        env_prefix = "REDIS_"


class JWTSettings(BaseSettings):
    SECRET_KEY: str = "your_default_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_prefix = "JWT_"


class CONFIG:
    NEO4J = Neo4jConfig()
    UVICORN = UvicornConfig()
    REDIS = RedisConfig()
    JWT = JWTSettings()
