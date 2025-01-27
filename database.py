from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .configuration import settings

connect_args = {}

if settings.sqlalchemy_database_url.startswith("sqlite:"):
    connect_args["check_same_thread"] = False

engine = create_engine(settings.sqlalchemy_database_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
