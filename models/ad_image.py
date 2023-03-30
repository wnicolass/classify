from datetime import datetime
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
    text
)
from sqlalchemy.orm import relationship
from config.database import Base

class AdImage(Base):
    __tablename__ = 'AdImage'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    image_name: str = Column(String(150), nullable = False)
    image_path_url: str = Column(String(150), nullable = False)
    ad_id: int = Column(Integer, ForeignKey('Ad.id', ondelete = 'CASCADE'))
    created_at: datetime = Column(DateTime, server_default = text('NOW()'))
    updated_at: datetime = Column(DateTime, onupdate = datetime.now())

    ad = relationship('Ad', back_populates = 'images', uselist = False)

