from typing import List
from sqlalchemy import and_, or_
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import (
    UserAccount
)
from models.chat import Chatroom, Message

# CREATE
async def send_message(
    buyer_user_id: int,
    seller_user_id: int,
    adv_id: int,
    text_message: str,
    session: AsyncSession
):
    chatroom = await get_chatroom_by_seller_and_buyer_id(
        seller_user_id, 
        buyer_user_id, 
        session
    )
    if not chatroom:
        chatroom = Chatroom(
            ad_id = adv_id, 
            starter_id = buyer_user_id,
            is_unread_receiver = 1,
            is_unread_starter = 0
        )
        session.add(chatroom)
        await session.commit()
        await session.refresh(chatroom)
        
    if buyer_user_id == chatroom.starter_id:
        chatroom.is_unread_receiver = 1
        chatroom.is_unread_starter = 0
        await session.commit()
        await session.refresh(chatroom)
    else:
        chatroom.is_unread_receiver = 0
        chatroom.is_unread_starter = 1
        await session.commit()
        await session.refresh(chatroom)

    message = Message(
        text_message = text_message,
        chatroom_id = chatroom.id,
        sender_user_id = buyer_user_id,
        receiver_user_id = seller_user_id,
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message

# READ
async def get_chatroom_by_seller_and_buyer_id(
    seller_user_id: int,
    buyer_user_id: int,
    session: AsyncSession
) -> Chatroom | None:
    query = await session.execute(
        select(Chatroom)
        .join(Chatroom.messages)
        .where(
            or_(and_(
                Message.sender_user_id == buyer_user_id,
                Message.receiver_user_id == seller_user_id,
            ),
            and_(
                Message.sender_user_id == seller_user_id,
                Message.receiver_user_id == buyer_user_id,
            )
        ))
        .limit(1)
    )
    chatroom = query.scalar_one_or_none()

    return chatroom

async def get_chatroom_by_id(
    chatroom_id: int,
    session: AsyncSession
):
    query = await session.execute(
        select(Chatroom)
        .where(Chatroom.id == chatroom_id)
    )
    chatroom = query.scalar_one_or_none() 

    return chatroom

async def get_senders_messages_by_current_user_id(
        current_user_id: int,
        session: AsyncSession
):
    chats_users_ids = (
        select(Message.receiver_user_id)
        .where(
            Message.sender_user_id == current_user_id,
        )
        .union(
            select(Message.sender_user_id)
            .where(
                Message.receiver_user_id == current_user_id,
            )
        )
        
    )
    messages = aliased(Message) # for join
    
    users = await session.execute(
        select(UserAccount)
        .outerjoin(Message, UserAccount.user_id == Message.sender_user_id)
        .outerjoin(messages, UserAccount.user_id == messages.receiver_user_id)
        .where(
            and_(
                UserAccount.user_id.in_(chats_users_ids),
                UserAccount.user_id != current_user_id
            )
        )
        .order_by(Message.send_at.desc()) # recent = desc
    )
    chat_users = users.unique().scalars().all()

    return chat_users

async def get_messages_by_chatroom_id(
    chatroom_id: int,
    session: AsyncSession
) -> List[Message]:
    query = await session.execute(
        select(Message)
        .join(Message.chatroom)
        .where(Chatroom.id == chatroom_id)
        .order_by(Message.send_at.asc()) # old = asc
    )
    messages = query.unique().scalars().all()

    return messages

# UPDATE
async def set_chatroom_as_read(
    chatroom_id: int,
    current_user_id: int,
    session: AsyncSession
):
    chatroom = await get_chatroom_by_id(chatroom_id, session)
    if chatroom.starter_id == current_user_id:
        chatroom.is_unread_starter = 0
    else:
        chatroom.is_unread_receiver = 0
    await session.commit()
