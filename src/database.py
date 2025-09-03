from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config import setting


SQL_ALCHEMY_DB_URL = (f"postgresql://{setting.DB_USER}:"
                      f"{setting.DB_PASSWORD}@{setting.DB_HOST}:"
                      f"{setting.DB_PORT}/{setting.DB_NAME}")

engine = create_engine(SQL_ALCHEMY_DB_URL, pool_size=setting.DB_POOL_SIZE,
                       max_overflow=setting.DB_MAX_OVERFLOW)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
