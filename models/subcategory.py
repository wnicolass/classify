from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)
from sqlalchemy.orm import relationship
from config.database import Base

class SubcategoryFieldDefinition(Base):
    __tablename__ = 'Subcategory_FieldDefinition'
    subcategory_id: int = Column(Integer, ForeignKey('Subcategory.subcategory_id'), primary_key = True, nullable = False)
    field_definition_id: int = Column(Integer, ForeignKey('FieldDefinition.field_definition_id'), primary_key = True, nullable = False)

    field_definition = relationship('FieldDefinition', back_populates = 'subcategories')
    subcategory = relationship('Subcategory', back_populates = 'field_definitions')


class Subcategory(Base):
    __tablename__ = 'Subcategory'

    subcategory_id: int = Column(Integer, primary_key = True, autoincrement = True)
    name: str = Column(String(40), nullable = False, unique = True)
    category_id: int = Column(Integer, ForeignKey('Category.category_id'), nullable = False)

    ads = relationship("Ad", back_populates = 'subcategory', cascade = 'delete')
    category = relationship("Category", back_populates = 'subcategories')
    field_definitions = relationship('SubcategoryFieldDefinition', back_populates = "subcategory")


