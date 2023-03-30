from sqlalchemy import (
    Column,
    Integer,
    String
)
from sqlalchemy.orm import relationship
from config.database import Base


class AdStatus(Base):
    __tablename__ = 'AdStatus'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    status_name: str = Column(String(30), nullable = False)
    status_description: str = Column(String(200), nullable = False)

    ads = relationship('Ad', back_populates = 'ad_status')