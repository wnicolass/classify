from sqlalchemy import (
    Column,
    Integer,
    String
)
from sqlalchemy.orm import relationship
from config.database import Base


class Condition(Base):
    __tablename__ = 'Condition'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    name: str = Column(String(30), nullable = False)
    description: str = Column(String(200), nullable = False)

    features = relationship('Feature', back_populates = 'condition')
    