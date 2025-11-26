"""Conversation API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.db.models.conversation import Conversation
from app.schemas.conversation import (
    ConversationThreadResponse,
    ConversationMessagesResponse
)

router = APIRouter()


@router.get("/user/{user_id}/threads", response_model=list[ConversationThreadResponse])
async def get_user_conversation_threads(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get all conversation threads for a user with the first message of each thread.
    Returns thread_id and the first message (user's initial query).
    """
    # Subquery to get the first message ID for each thread
    subquery = (
        select(
            Conversation.thread_id,
            func.min(Conversation.id).label("first_message_id")
        )
        .where(Conversation.user_id == user_id)
        .group_by(Conversation.thread_id)
        .subquery()
    )
    
    # Get the actual first messages
    stmt = (
        select(Conversation)
        .join(
            subquery,
            (Conversation.thread_id == subquery.c.thread_id) &
            (Conversation.id == subquery.c.first_message_id)
        )
        .order_by(Conversation.created_at.desc())
    )
    
    result = await db.execute(stmt)
    conversations = result.scalars().all()
    
    return [
        {
            "thread_id": conv.thread_id,
            "first_message": conv.message,
            "created_at": conv.created_at
        }
        for conv in conversations
    ]


@router.get("/thread/{thread_id}", response_model=ConversationMessagesResponse)
async def get_conversation_messages(
    thread_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all messages for a specific conversation thread.
    Returns messages in chronological order (human -> ai -> human -> ai).
    """
    stmt = (
        select(Conversation)
        .where(Conversation.thread_id == thread_id)
        .order_by(Conversation.created_at)
    )
    
    result = await db.execute(stmt)
    messages = result.scalars().all()
    
    if not messages:
        raise HTTPException(status_code=404, detail="Conversation thread not found")
    
    return {
        "thread_id": thread_id,
        "user_id": messages[0].user_id,
        "messages": [
            {
                "id": msg.id,
                "message_type": msg.message_type,
                "message": msg.message,
                "created_at": msg.created_at
            }
            for msg in messages
        ],
        "total_messages": len(messages)
    }
