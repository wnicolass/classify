from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from config.database import Base

class Address(Base):
    __tablename__ = "Address"

    address_id: int = Column(Integer, primary_key = True, autoincrement = True)
    country: str = Column(String(40), nullable = False)
    city: str = Column(String(40), nullable = False, index = True)
    street: str = Column(String(60), nullable = False)
    number: int = Column(Integer, nullable = False)
    user_id: int = Column(Integer, ForeignKey("User.user_id", ondelete = 'CASCADE'), nullable = False)
    address_date: datetime = Column(DateTime, default = datetime.now())

    user = relationship("User", back_populates = "address")