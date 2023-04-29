from config.database import Base
from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    ForeignKey,
    String,
    text
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import BIT

class Message(Base):
    __tablename__ = 'Message'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    text_message: str = Column(String(500), nullable = False)
    send_at: datetime = Column(DateTime, server_default = text('NOW()'))
    
    chatroom_id: int = Column(
        Integer, 
        ForeignKey('Chatroom.id'), 
        nullable = False
    )
    sender_user_id: int = Column(
        Integer, 
        ForeignKey('UserAccount.user_id'), 
        nullable = False
    )
    receiver_user_id: int = Column(
        Integer, 
        ForeignKey('UserAccount.user_id'), 
        nullable = False
    )

    receiver_user = relationship(
        'UserAccount', 
        back_populates = 'messages_received',
        foreign_keys = [receiver_user_id],
        uselist = False,
        lazy = 'joined'
    )
    sender_user = relationship(
        'UserAccount', 
        back_populates = 'messages_sent',
        foreign_keys = [sender_user_id],
        uselist = False,
        lazy = 'joined'
    )
    chatroom = relationship(
        'Chatroom', 
        back_populates = 'messages', 
        lazy = 'joined'
    )

class Chatroom(Base):
    __tablename__ = 'Chatroom'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    starter_id: int = Column(
        Integer, 
        ForeignKey('UserAccount.user_id'), 
        nullable = False
    )
    is_unread_starter: bool = Column(BIT)
    is_unread_receiver: bool = Column(BIT)
    created_at: datetime = Column(DateTime, server_default = text('NOW()'))

    ad_id: int = Column(Integer, ForeignKey('Ad.id'))

    starter_user = relationship(
        'UserAccount', 
        back_populates = 'chatrooms',
        uselist = False,
        lazy = 'joined'
    )
    messages = relationship('Message', back_populates = 'chatroom')
    ad = relationship('Ad', back_populates = 'chatrooms')