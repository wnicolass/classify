from datetime import datetime
from decimal import Decimal as dec
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
    DECIMAL,
    Enum
)
from sqlalchemy.orm import relationship
from config.database import Base

class FieldValue(Base):
    __tablename__ = 'FieldValue'
    field_definition_id: int = Column(Integer, ForeignKey('FieldDefinition.field_definition_id'), primary_key = True)
    ad_id: int = Column(Integer, ForeignKey('Ad.ad_id'), primary_key = True)
    value: str = Column(String(100), nullable = False)

    ad = relationship('Ad', back_populates = 'field_definitions')
    field_definition = relationship('FieldDefinition', back_populates = 'ads')


class Ad(Base):
    __tablename__ = 'Ad'

    ad_id: int = Column(Integer, primary_key = True, autoincrement = True)
    title: str = Column(String(200), nullable = False, unique = True)
    description: str = Column(String(1000), nullable = False)
    price: dec = Column(DECIMAL(8,2), nullable = False)
    product_name: str = Column(String(100), nullable = False)
    status: str = Column(Enum('active', 'inactive', 'sold', 'expired', 'deleted'), nullable = False)
    views: int = Column(Integer, default = 0, nullable = False)
    negotiable: str = Column(Enum('Yes', 'No'), nullable = False)
    feature_id: int = Column(Integer, ForeignKey('Feature.feature_id'), nullable = False)
    user_id: int = Column(Integer, ForeignKey('User.user_id', ondelete = 'CASCADE'), nullable = False)
    subcategory_id: int = Column(Integer, ForeignKey('Subcategory.subcategory_id'), nullable = False)
    created_at: datetime = Column(DateTime, default = datetime.now())

    user = relationship('User', back_populates = 'ads')
    feature = relationship('Feature')
    subcategory = relationship('Subcategory', back_populates = 'ads')
    field_definitions = relationship('FieldValue', back_populates = 'ad')
    admins = relationship('AdApproval', back_populates = 'ad')
