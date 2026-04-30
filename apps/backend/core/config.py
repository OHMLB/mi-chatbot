from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=BASE_DIR /".env",
        env_ignore_empty=True,
    )

    AZ_PATH: str
    AZ_WEBSV: str

settings = Settings()
