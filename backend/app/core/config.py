from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "Voice2Minutes API"
    APP_VERSION: str = "0.1.0"

    RTZR_CLIENT_ID: str
    RTZR_CLIENT_SECRET: str

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()