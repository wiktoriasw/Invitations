from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .configuration import settings

engine = create_engine(
    settings.sqlalchemy_database_url, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
