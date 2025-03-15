import os

from functools import lru_cache

from dotenv import load_dotenv
from pathlib import Path

from pydantic_settings import BaseSettings

# Define the logs directory path
PROJECT_DIR = Path(__file__).parent.parent

# Define the application directory
APP_DIR = PROJECT_DIR / "app"

# Load environment variables from .env file
load_dotenv(f"{APP_DIR}/.env")


class Settings(BaseSettings):
    DB_HOST: str | None = os.getenv("DB_HOST")
    DB_PORT: str | None = os.getenv("DB_PORT")
    DB_USER: str | None = os.getenv("DB_USER")
    DB_PASSWORD: str | None = os.getenv("DB_PASSWORD")
    DB_NAME: str | None = os.getenv("POSTGRES_DB")
    DB_DRIVER: str | None = os.getenv("DB_DRIVER")

    SQLALCHEMY_DB_URL: str = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
