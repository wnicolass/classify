from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)
from sqlalchemy.orm import relationship
from config.database import Base

class Feature(Base):
    __tablename__ = 'Feature'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    brand: str = Column(String(30), nullable = False, index = True)
    authenticity: str = Column(String(50), nullable = False)
    condition_id: str = Column(Integer, ForeignKey('Condition.id'), nullable = False)

    condition = relationship('Condition', back_populates = 'features', uselist = False)
    ad = relationship('Ad', back_populates = 'feature', uselist = False)
    