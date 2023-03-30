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

class AdAddress(Base):
    __tablename__ = "AdAddress"

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    country: str = Column(String(40), nullable = False)
    city: str = Column(String(40), nullable = False, index = True)
    street: str = Column(String(60), nullable = False)
    number: int = Column(Integer, nullable = False)
    postal_code: str = Column(String(50), nullable = False)
    address_date: datetime = Column(DateTime, server_default = text('NOW()'))
    updated_at: datetime = Column(DateTime, onupdate = datetime.now())

    ads = relationship("Ad", cascade = 'delete', back_populates = "address")