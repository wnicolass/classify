from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table
)
from sqlalchemy.orm import relationship
from config.database import Base
from models.category import Category
from models.field_value import field_value

subcategory_field_definition = Table(
    'Subcategory_FieldDefinition',
    Base.metadata,
    Column("subcategory_id", Integer, ForeignKey('Subcategory.id'), primary_key = True, nullable = False),
    Column("field_definition_id", Integer, ForeignKey('FieldDefinition.id'), primary_key = True, nullable = False)
)

class Subcategory(Base):
    __tablename__ = 'Subcategory'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    subcategory_name: str = Column(String(40), nullable = False, unique = True)
    category_id: int = Column(Integer, ForeignKey('Category.id', ondelete = 'CASCADE'), nullable = False)

    ads = relationship("Ad", back_populates = 'subcategory', lazy = 'joined')
    category = relationship("Category", back_populates = 'subcategories')
    field_definitions = relationship('FieldDefinition', secondary = subcategory_field_definition, back_populates = 'subcategories')

    @property
    def count_total_ads(self) -> int:
        return len(self.ads)

class FieldDefinition(Base):
    __tablename__ = "FieldDefinition"

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    field_name: str = Column(String(30), nullable = False, unique = True)
    field_type: str = Column(String(30), nullable = False)

    subcategories = relationship('Subcategory', secondary = subcategory_field_definition, back_populates = 'field_definitions')
    ads = relationship('Ad', secondary = field_value, back_populates = 'field_definitions')


