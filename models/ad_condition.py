from sqlalchemy import (
    Column,
    Integer,
    String
)
from sqlalchemy.orm import relationship
from config.database import Base


class AdCondition(Base):
    __tablename__ = 'AdCondition'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    condition_name: str = Column(String(30), nullable = False)
    condition_description: str = Column(String(200), nullable = False)

    features = relationship('Feature', back_populates = 'condition')
    