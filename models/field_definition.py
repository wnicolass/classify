from sqlalchemy import (
    Column,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from config.database import Base

class FieldDefinition(Base):
    __tablename__ = "FieldDefinition"

    field_definition_id: int = Column(Integer, primary_key = True, autoincrement = True)
    name: str = Column(String(30), nullable = False, unique = True)
    type: str = Column(String(30), nullable = False)

    subcategories = relationship('SubcategoryFieldDefinition', back_populates = 'field_definition')
    ads = relationship('FieldValue', back_populates = 'field_definition')