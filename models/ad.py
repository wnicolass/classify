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
    text,
)
from sqlalchemy.dialects.mysql import BIT
from sqlalchemy.orm import relationship, joinedload
from config.database import Base
from models.ad_approval import ad_approval
from models.subcategory import Subcategory
from models.field_value import field_value
from models.admin import AdminAccount

class Ad(Base):
    __tablename__ = 'Ad'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    title: str = Column(String(200), nullable = False)
    ad_description: str = Column(String(1000), nullable = False)
    price: dec = Column(DECIMAL(8,2), nullable = False)
    views: int = Column(Integer, default = 0, nullable = False)
    is_negotiable: int = Column(BIT, nullable = False)
    
    status_id: str = Column(Integer, ForeignKey('AdStatus.id'), nullable = False)
    feature_id: int = Column(Integer, ForeignKey('Feature.id'), nullable = False)
    user_id: int = Column(Integer, ForeignKey('UserAccount.user_id', ondelete = 'CASCADE'), nullable = False)
    ad_address_id: int = Column(Integer, ForeignKey('AdAddress.id'), nullable = False)
    subcategory_id: int = Column(Integer, ForeignKey('Subcategory.id'), nullable = False)
    
    created_at: datetime = Column(DateTime, server_default = text('NOW()'))
    updated_at: datetime = Column(DateTime, onupdate = datetime.now())

    address = relationship('AdAddress', back_populates = 'ads', uselist = False, lazy = 'joined')
    user = relationship('UserAccount', back_populates = 'ads', lazy = 'joined')
    feature = relationship('Feature', back_populates = 'ad', uselist = False, lazy = 'joined')
    subcategory = relationship('Subcategory', back_populates = 'ads', lazy = 'joined')
    field_definitions = relationship('FieldDefinition', secondary = field_value, back_populates = 'ads')
    admin = relationship('AdminAccount', secondary = ad_approval, back_populates = 'ads', uselist = False)
    ad_status = relationship('AdStatus', back_populates = 'ads', uselist = False, lazy = 'joined')
    images = relationship('AdImage', back_populates = 'ad', cascade = 'delete', lazy = 'joined')
    users_favourited = relationship('Favourites', back_populates = 'ad')


    @property
    def main_image(self):
        return self.images[0].image_path_url

    @property
    def pretty_date(self):
        return datetime.strftime(self.created_at, '%d %b, %Y')

    @property
    def condition(self):
        return self.feature.condition.condition_name
    
class Feature(Base):
    __tablename__ = 'Feature'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    brand: str = Column(String(30), nullable = False, index = True)
    authenticity: str = Column(String(50), nullable = False)
    condition_id: str = Column(Integer, ForeignKey('AdCondition.id'), nullable = False)

    condition = relationship('AdCondition', back_populates = 'features', uselist = False, lazy = 'joined')
    ad = relationship('Ad', back_populates = 'feature', uselist = False)

class AdCondition(Base):
    __tablename__ = 'AdCondition'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    condition_name: str = Column(String(30), nullable = False)
    condition_description: str = Column(String(200), nullable = False)

    features = relationship('Feature', back_populates = 'condition', lazy = 'joined')

class AdAddress(Base):
    __tablename__ = "AdAddress"

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    country: str = Column(String(40), nullable = False)
    city: str = Column(String(40), nullable = False, index = True)
    address_date: datetime = Column(DateTime, server_default = text('NOW()'))
    updated_at: datetime = Column(DateTime, onupdate = datetime.now())

    ads = relationship("Ad", back_populates = "address")

class AdStatus(Base):
    __tablename__ = 'AdStatus'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    status_name: str = Column(String(30), nullable = False)
    status_name_internal: str = Column(String(30), nullable = False)
    status_description: str = Column(String(200), nullable = False)

    ads = relationship('Ad', back_populates = 'ad_status')

class AdImage(Base):
    __tablename__ = 'AdImage'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    image_name: str = Column(String(150), nullable = False)
    image_path_url: str = Column(String(150), nullable = False)
    ad_id: int = Column(Integer, ForeignKey('Ad.id', ondelete = 'CASCADE'))
    created_at: datetime = Column(DateTime, server_default = text('NOW()'))
    updated_at: datetime = Column(DateTime, onupdate = datetime.now())

    ad = relationship('Ad', back_populates = 'images', uselist = False)
    
