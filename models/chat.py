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

class Message(Base):
    __tablename__ = 'Message'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    text_message: str = Column(String(500), nullable = False)
    send_at: datetime = Column(DateTime, server_default = text('NOW()'))
    
    chatroom_id: int = Column(Integer, ForeignKey('Chatroom.id'), nullable = False)
    sender_user_id: int = Column(Integer, ForeignKey('UserAccount.user_id'), nullable = False)
    receiver_user_id: int = Column(Integer, ForeignKey('UserAccount.user_id'), nullable = False)

    receiver_user = relationship(
        'UserAccount', 
        back_populates = 'messages_received',
        foreign_keys = [receiver_user_id],
        uselist = False
    )
    sender_user = relationship(
        'UserAccount', 
        back_populates = 'messages_sent',
        foreign_keys = [sender_user_id],
        uselist = False
    )
    chatroom = relationship('Chatroom', back_populates = 'messages')

class Chatroom(Base):
    __tablename__ = 'Chatroom'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    created_at: datetime = Column(DateTime, server_default = text('NOW()'))

    ad_id: int = Column(Integer, ForeignKey('Ad.id'))

    messages = relationship('Message', back_populates = 'chatroom')
    ad = relationship('Ad', back_populates = 'chatrooms')