from sqlalchemy import (
    Column,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from config.database import Base
from models.subcategory import subcategory_field_definition
from models.ad import field_value

class FieldDefinition(Base):
    __tablename__ = "FieldDefinition"

    field_definition_id: int = Column(Integer, primary_key = True, autoincrement = True)
    name: str = Column(String(30), nullable = False, unique = True)
    type: str = Column(String(30), nullable = False)

    subcategories = relationship('Subcategory', secondary = subcategory_field_definition, back_populates = 'field_definitions')
    ads = relationship('Ad', secondary = field_value, back_populates = 'field_definitions')