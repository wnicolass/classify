from datetime import datetime
from decimal import Decimal as dec
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
    Table,
    DECIMAL,
    text
)
from sqlalchemy.dialects.mysql import BIT
from sqlalchemy.orm import relationship
from config.database import Base
from models.ad_approval import ad_approval

field_value = Table(
    'FieldValue',
    Base.metadata,
    Column('field_definition_id', Integer, ForeignKey('FieldDefinition.id'), primary_key = True),
    Column('ad_id', Integer, ForeignKey('Ad.id'), primary_key = True),
    Column('value', String(100), nullable = False),
)

class Ad(Base):
    __tablename__ = 'Ad'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    title: str = Column(String(200), nullable = False, unique = True)
    description: str = Column(String(1000), nullable = False)
    price: dec = Column(DECIMAL(8,2), nullable = False)
    product_name: str = Column(String(100), nullable = False)
    ad_image_url: str = Column(String(100), nullable = False)
    views: int = Column(Integer, default = 0, nullable = False)
    negotiable: str = Column(BIT, nullable = False)
    
    status_id: str = Column(Integer, ForeignKey('AdStatus.id'), nullable = False)
    feature_id: int = Column(Integer, ForeignKey('Feature.id'), nullable = False)
    user_id: int = Column(Integer, ForeignKey('UserAccount.user_id', ondelete = 'CASCADE'), nullable = False)
    ad_address_id: int = Column(Integer, ForeignKey('AdAddress.id'), nullable = False)
    subcategory_id: int = Column(Integer, ForeignKey('Subcategory.id'), nullable = False)
    
    created_at: datetime = Column(DateTime, server_default = text('NOW()'))
    updated_at: datetime = Column(DateTime, onupdate = datetime.now())

    address = relationship('AdAddress', back_populates = 'address', cascade = 'delete', uselist = False)
    user = relationship('UserAccount', back_populates = 'ads')
    feature = relationship('Feature', back_populates = 'ad', uselist = False)
    subcategory = relationship('Subcategory', back_populates = 'ads')
    field_definitions = relationship('FieldDefinition', secondary = field_value, back_populates = 'ads')
    admin = relationship('AdminAccount', secondary = ad_approval, back_populates = 'ads')
    ad_status = relationship('AdStatus', back_populates = 'ads', uselist = False)
