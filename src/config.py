from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_env_file() -> Path | None:
  """
  Search for a .env file starting from this file's directory and walking up
  the directory tree. Returns the first match or None if not found.
  """
  start = Path(__file__).resolve().parent
  for parent in [start, *start.parents]:
    candidate = parent / ".env"
    if candidate.exists():
      return candidate
  return None


class Settings(BaseSettings):
  # Database settings
  DB_HOST: str
  DB_NAME: str
  DB_USER: str
  DB_PASSWORD: str
  DB_PORT: int = 5432
  DB_POOL_SIZE: int = 5
  DB_MAX_OVERFLOW: int = 10

  # Application settings
  API_V1_STR: str = "/api/v1"
  PROJECT_NAME: str = "Neotech Assignment"
  DEBUG: bool = False

  # ... existing code ...
  model_config = SettingsConfigDict(
    env_file=_find_env_file(), env_file_encoding="utf-8"
  )


# ... existing code ...
settings = Settings()
