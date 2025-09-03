from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
  # Database settings
  DB_HOST: str
  DB_NAME: str
  DB_USER: str
  DB_PASSWORD: str
  DB_PORT: int = 5432
  DB_POOL_SIZE: int
  DB_MAX_OVERFLOW: int

  # Application settings
  API_V1_STR: str = "/api/v1"
  PROJECT_NAME: str = "Neotech Assignment"
  DEBUG: bool = False

  class Config:
    env_file = Path(__file__).resolve().parent / ".env"
    print(f'environment created - {Path(Path(__file__).resolve().name)}')


setting = Settings()
