from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    text
)
from sqlalchemy.orm import relationship
from config.database import Base


class HashAlgo(Base):
    __tablename__ = 'HashAlgo'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    hash_name: str = Column(String(50), nullable = False)
    created_at: datetime = Column(DateTime, server_default = text('NOW()'))

    users = relationship('UserLoginData', back_populates = 'hash')
