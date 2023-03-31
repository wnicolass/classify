from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String
)
from sqlalchemy.orm import relationship
from config.database import Base


class EmailValidationStatus(Base):
    __tablename__ = 'EmailValidationStatus'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    status_name: str = Column(String(30))

    users = relationship('UserLoginData', back_populates = 'email_status')