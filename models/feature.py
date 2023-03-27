from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum
)
from config.database import Base

class Feature(Base):
    __tablename__ = 'Feature'

    feature_id: int = Column(Integer, primary_key = True, autoincrement = True)
    brand: str = Column(String(30), nullable = False, index = True)
    condition: str = Column(Enum("used", "refurbished", "brand-new"), nullable = False)
    authenticity: str = Column(String(50), nullable = False)