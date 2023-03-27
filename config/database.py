import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from sqlalchemy.future import Engine
from sqlalchemy.ext.declarative import declarative_base

load_dotenv(find_dotenv())

engine: Engine = create_engine(url = os.getenv('CONNECTION_STRING'), echo = False)
DbSession: Session = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine
)
Base = declarative_base()

def create_metadata() -> None:
    import models.__all_models

    Base.metadata.drop_all(bind = engine)
    Base.metadata.create_all(bind = engine)

