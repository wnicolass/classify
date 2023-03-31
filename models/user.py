from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Date,
    ForeignKey,
    Table,
    text,
)
from sqlalchemy.dialects.mysql import BIT
from sqlalchemy.orm import relationship
from config.database import Base


user_login_data_ext = Table(
    'UserLoginDataExt',
    Base.metadata,
    Column('id', Integer, primary_key = True, autoincrement = True),
    Column('external_provider_token', String(200), nullable = False),
    Column('external_provider_id', Integer, ForeignKey('ExternalProvider.id'), nullable = False),
    Column('user_id', Integer, ForeignKey('UserAccount.user_id'), nullable = False),
)


class UserAccount(Base):
    __tablename__ = 'UserAccount'

    user_id: int = Column(Integer, primary_key = True, autoincrement = True)
    username: str = Column(String(100), nullable = False)
    phone_number: str = Column(String(12), nullable = False)
    birth_date: datetime = Column(Date, nullable = False)
    last_login: datetime = Column(DateTime, server_default = text('NOW()'))
    profile_image_url: str = Column(String(100))
    is_active: int = Column(BIT, nullable = False)

    created_at: datetime = Column(DateTime, server_default = text('NOW()'))

    ads = relationship('Ad', back_populates = 'user', cascade = "delete")
    user_address = relationship('UserAddress', back_populates = 'user', cascade = "delete", uselist = False)
    user_login_data = relationship('UserLoginData', back_populates = 'user', uselist = False)
    user_login_data_exts = relationship('UserLoginDataExt', back_populates = 'user')
    ext_provider = relationship('ExternalProvider', back_populates = 'user', secondary = user_login_data_ext)

    @property
    def email_addrs(self) -> str:
        return self.user_login_data.email_addr

class UserLoginData(Base):
    __tablename__ = 'UserLoginData'

    user_id: int = Column(Integer, ForeignKey('UserAccount.user_id'), primary_key = True)
    password_hash: str = Column(String(50), nullable = False)
    password_salt: str = Column(String(50), nullable = False)
    email_addr: str = Column(String(320), nullable = False)
    confirm_token: str = Column(String(200), nullable = True)
    confirm_token_time: str = Column(String(50), nullable = True)
    recovery_token: str = Column(String(200), nullable = True)
    recovery_token_time: str = Column(String(50), nullable = True)

    hash_algo_id: int = Column(Integer, ForeignKey('HashAlgo.id'), nullable = False)
    email_validation_status_id: int = Column(Integer, ForeignKey('EmailValidationStatus.id'), nullable = False)

    user = relationship('UserAccount', back_populates = 'user_login_data', uselist = False)
    hash = relationship('HashAlgo', back_populates = 'users', uselist = False)
    email_status = relationship('EmailValidationStatus', back_populates = 'users', uselist = False)