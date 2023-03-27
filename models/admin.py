from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime
)
from sqlalchemy.orm import relationship
from config.database import Base

class Admin(Base):
    __tablename__ = 'Admin'

    admin_id: int = Column(Integer, autoincrement = True, primary_key = True)
    first_name: str = Column(String(30), nullable = False)
    last_name: str = Column(String(30), nullable = False)
    email: str = Column(String(50), nullable = False, unique = True)
    hashed_password: str = Column(String(100), nullable = False)
    phone_number: str = Column(String(12), nullable = False)
    created_at: datetime = Column(DateTime, default = datetime.now())

    ads = relationship('AdApproval', back_populates = 'admin')
    