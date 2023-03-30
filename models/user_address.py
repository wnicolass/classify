from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    text
)
from sqlalchemy.orm import relationship
from config.database import Base

class UserAddress(Base):
    __tablename__ = "UserAddress"

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    country: str = Column(String(50), nullable = False)
    city: str = Column(String(50), nullable = False, index = True)
    street: str = Column(String(200), nullable = False)
    num: str = Column(String(20), nullable = False)
    postal_code: str = Column(String(50), nullable = False)
    user_id: int = Column(Integer, ForeignKey("UserAccount.user_id", ondelete = 'CASCADE'), nullable = False)
    address_date: datetime = Column(DateTime, server_default = text('NOW()'))
    updated_at: datetime = Column(DateTime, onupdate = datetime.now())

    user = relationship("UserAccount", back_populates = "user_address")