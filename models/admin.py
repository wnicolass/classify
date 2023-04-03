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
from models.ad_approval import ad_approval

class AdminAccount(Base):
    __tablename__ = 'AdminAccount'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    admin_name: str = Column(String(100), nullable = False)
    email: str = Column(String(320), nullable = False)
    password_hash: str = Column(String(50), nullable = False)
    password_salt: str = Column(String(50), nullable = False)
    phone_number: str = Column(String(12), nullable = False)

    created_at: datetime = Column(DateTime, server_default = text('NOW()'))

    ads = relationship('Ad', secondary = ad_approval, back_populates = 'admin')
    