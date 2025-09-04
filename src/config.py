import os
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_env_file() -> Path | None:
  start = Path(__file__).resolve().parent
  for parent in [start, *start.parents]:
    candidate = parent / ".env"
    if candidate.exists():
      return candidate
  return None


class Settings(BaseSettings):
  ENVIRONMENT: str = Field("local", description="Set 'local' or 'azure'")

  # Database settings
  DB_HOST: str = "localhost"
  DB_NAME: str = "neotech"
  DB_USER: str = "postgres"
  DB_PASSWORD: str = "postgres"
  DB_PORT: int = 5432

  API_V1_STR: str = "/api/v1"
  PROJECT_NAME: str = "Neotech Assignment"
  DEBUG: bool = False

  model_config = SettingsConfigDict(
    env_file=_find_env_file(), env_file_encoding="utf-8", extra="ignore"
  )

  @field_validator("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD", mode="before")
  @classmethod
  def switch_db_for_environment(cls, v, info):
    env = info.data.get("ENVIRONMENT", "local")
    if env.lower() == "azure":
      azure_map = {
        "DB_HOST": os.getenv("AZURE_DB_HOST"),
        "DB_NAME": os.getenv("AZURE_DB_NAME"),
        "DB_USER": os.getenv("AZURE_DB_USER"),
        "DB_PASSWORD": os.getenv("AZURE_DB_PASSWORD"),
      }
      return azure_map.get(info.field_name, v) or v
    return v


settings = Settings()
