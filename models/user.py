from datetime import datetime
from typing import List
from urllib.parse import unquote_plus
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Date,
    ForeignKey,
    text,
)
from sqlalchemy.dialects.mysql import BIT
from sqlalchemy.orm import relationship
from urllib.parse import unquote_plus
from config.database import Base
from models.ad import Ad
from services.ad_service import AdStatusEnum
from common.utils import image_formats, transform_image_from_url
from models.chat import Message

class UserAccount(Base):
    __tablename__ = 'UserAccount'

    user_id: int = Column(Integer, primary_key = True, autoincrement = True)
    username: str = Column(String(100), nullable = False)
    phone_number: str = Column(String(12), nullable = True)
    birth_date: datetime = Column(Date, nullable = True)
    last_login: datetime = Column(DateTime, server_default = text('NOW()'))
    profile_image_url: str = Column(String(1000))
    is_active: int = Column(BIT, nullable = False)

    created_at: datetime = Column(DateTime, server_default = text('NOW()'))

    ads = relationship('Ad', back_populates = 'user', cascade = "delete")
    user_address = relationship(
        'UserAddress', 
        back_populates = 'user', 
        cascade = "delete", 
        uselist = False
    )
    user_login_data = relationship(
        'UserLoginData', 
        back_populates = 'user', 
        uselist = False
    )
    user_login_data_ext = relationship(
        'UserLoginDataExt', 
        back_populates = 'user'
    )
    favourites = relationship('Favourite', back_populates = 'user')
    favourite_searches = relationship(
        'FavouriteSearch', 
        back_populates = 'user'
    )
    
    messages_received = relationship(
        'Message', 
        back_populates = 'receiver_user',
        foreign_keys = [Message.receiver_user_id]
    )
    messages_sent = relationship(
        'Message', 
        back_populates = 'sender_user', 
        foreign_keys = [Message.sender_user_id]
    )
    chatrooms = relationship('Chatroom', back_populates = 'starter_user')

    @property
    def pretty_created_at(self):
        return datetime.strftime(self.created_at, '%Y')

    @property
    def email_addrs(self) -> str:
        return self.user_login_data.email_addr
    
    @property
    def fav_ads_id(self) -> List[int]:
        return [fav.ad_id for fav in self.favourites]
    
    @property
    def active_favs(self) -> List['Favourite']:
        return [
            fav for fav in self.favourites 
            if fav.ad.status_id == AdStatusEnum.ACTIVE.value
        ]
    
    @property
    def inactive_favs(self) -> List['Favourite']:
        inactive_ads = []
        for fav in self.favourites:
            is_expired_ad = fav.ad.status_id == AdStatusEnum.EXPIRED.value
            is_sold_ad = fav.ad.status_id == AdStatusEnum.SOLD.value
            if is_expired_ad or is_sold_ad:
                inactive_ads.append(fav)
        return inactive_ads
    
    @property
    def profile_image_squared(self) -> str:
        return transform_image_from_url(
            self.profile_image_url, 
            image_formats["square_fill"]
        )

class UserLoginData(Base):
    __tablename__ = 'UserLoginData'

    user_id: int = Column(
        Integer, 
        ForeignKey('UserAccount.user_id'), 
        primary_key = True
    )
    password_hash: str = Column(String(300), nullable = True)
    password_salt: str = Column(String(300), nullable = True)
    email_addr: str = Column(String(320), nullable = False, unique = True)
    confirm_token: str = Column(String(200), nullable = True)
    confirm_token_time: str = Column(String(50), nullable = True)
    recovery_token: str = Column(String(200), nullable = True)
    recovery_token_time: str = Column(String(50), nullable = True)

    hash_algo_id: int = Column(
        Integer, 
        ForeignKey('HashAlgo.id'), 
        nullable = True
    )
    email_validation_status_id: int = Column(
        Integer, 
        ForeignKey('EmailValidationStatus.id'), 
        nullable = False
    )

    user = relationship(
        'UserAccount', 
        back_populates = 'user_login_data', 
        uselist = False, 
        lazy = 'joined'
    )
    hash = relationship('HashAlgo', back_populates = 'users', uselist = False)
    email_status = relationship(
        'EmailValidationStatus', 
        back_populates = 'users', 
        uselist = False
    )

    @property
    def is_active(self) -> int:
        return self.user.is_active

class UserAddress(Base):
    __tablename__ = "UserAddress"

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    country: str = Column(String(50), nullable = False)
    city: str = Column(String(50), nullable = False, index = True)
    user_id: int = Column(
        Integer, 
        ForeignKey("UserAccount.user_id", ondelete = 'CASCADE'), 
        nullable = False
    )
    address_date: datetime = Column(DateTime, server_default = text('NOW()'))
    updated_at: datetime = Column(DateTime, onupdate = datetime.now())

    user = relationship("UserAccount", back_populates = "user_address")

class ExternalProvider(Base):
    __tablename__ = 'ExternalProvider'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    ext_provider_name: str = Column(String(50), nullable = False)
    end_point_url: str = Column(String(100), nullable = False)

    user_login_data_ext = relationship(
        'UserLoginDataExt', 
        back_populates = 'ext_provider'
    )

class UserLoginDataExt(Base):
    __tablename__ = 'UserLoginDataExt'
    
    id: int = Column(Integer, primary_key = True, autoincrement = True)
    external_provider_token: str = Column(String(1200), nullable = False)
    external_provider_id: int = Column(
        Integer, 
        ForeignKey('ExternalProvider.id'), 
        nullable = False
    )
    user_id: int = Column(
        Integer, 
        ForeignKey('UserAccount.user_id'), 
        nullable = False
    )

    ext_provider = relationship(
        'ExternalProvider', 
        back_populates = 'user_login_data_ext'
    )
    user = relationship(
        'UserAccount', 
        back_populates = 'user_login_data_ext', 
        lazy = 'joined'
    )

class Favourite(Base):
    __tablename__ = 'Favourite'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    user_id: int = Column(
        Integer, 
        ForeignKey('UserAccount.user_id'), 
        nullable = False
    )
    ad_id: int = Column(Integer, ForeignKey('Ad.id'), nullable = False)
    fav_date: datetime = Column(DateTime, default = datetime.now())

    user = relationship(
        'UserAccount', 
        back_populates = 'favourites', 
        uselist = False
    )
    ad = relationship(
        'Ad', 
        back_populates = 'users_favourited', 
        uselist = False, 
        lazy = 'joined'
    )

class FavouriteSearch(Base):
    __tablename__ = 'FavouriteSearch'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    user_id: int = Column(
        Integer, 
        ForeignKey('UserAccount.user_id'), 
        nullable = False
    )
    search_url: str = Column(String(500), nullable = False)
    search_description: int = Column(BIT, default = 0)
    category: str = Column(String(100), default = "Nenhuma")
    subcategory: str = Column(String(100), default = "Nenhuma")
    order_type: str = Column(String(100), default = "Nenhuma")
    fav_date: datetime = Column(DateTime, default = datetime.now())

    user = relationship(
        'UserAccount', 
        back_populates = 'favourite_searches', 
        uselist = False
    )

    @property
    def search_title(self) -> str:
        title = 'Pesquisa sem título'
        equal_sign_index = self.search_url.index('=')
        try:
            if self.search_url[equal_sign_index + 1] != '&':
                temp_title = []
                for i in range(equal_sign_index + 1, len(self.search_url)):
                    if self.search_url[i] == '&':
                        break
                    temp_title.append(self.search_url[i])
                temp_title = ''.join(temp_title)
                if not temp_title.isdigit():
                    title = temp_title
            return unquote_plus(title)
        except IndexError:
            return unquote_plus(title)
        
    @property
    def search_description_text(self) -> str:
        if self.search_description == 1:
            return "Sim"
        return "Não"

class HashAlgo(Base):
    __tablename__ = 'HashAlgo'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    hash_name: str = Column(String(50), nullable = False)
    created_at: datetime = Column(DateTime, server_default = text('NOW()'))

    users = relationship('UserLoginData', back_populates = 'hash')

class EmailValidationStatus(Base):
    __tablename__ = 'EmailValidationStatus'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    status_name: str = Column(String(30))

    users = relationship('UserLoginData', back_populates = 'email_status')

class OpenIdConnectTokens(Base):
    __tablename__ = 'OpenIdConnectTokens'

    state: str = Column(String(256), nullable = False, primary_key = True)
    nonce: str = Column(String(1000), nullable = False)