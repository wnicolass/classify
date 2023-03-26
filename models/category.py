from sqlalchemy import (
    Column,
    Integer,
    String
)
from sqlalchemy.orm import relationship
from config.database import Base

class Category(Base):
    __tablename__ = "Category"

    category_id: int = Column(Integer, primary_key = True, autoincrement = True)
    name: str = Column(String(30), nullable = False, index = True)

    subcategories = relationship('Subcategory', back_populates = 'category', cascade = 'delete')
