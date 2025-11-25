"""Conversation history management."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.conversation import Conversation
from app.core.logging import get_logger

logger = get_logger(__name__)


class ConversationHistory:
    """Manages conversation history storage."""
    
    @staticmethod
    async def save_message(
        db: AsyncSession,
        thread_id: str,
        user_id: int,
        message: str,
        message_type: str
    ) -> Conversation:
        """Save a conversation message."""
        conversation = Conversation(
            thread_id=thread_id,
            user_id=user_id,
            message=message,
            message_type=message_type
        )
        
        db.add(conversation)
        await db.flush()
        
        logger.debug(f"Saved {message_type} message for thread {thread_id[:8]}...")
        return conversation
    
    @staticmethod
    async def get_thread_history(
        db: AsyncSession,
        thread_id: str,
        limit: int = 50
    ) -> list[Conversation]:
        """Get conversation history for a thread."""
        stmt = select(Conversation).where(
            Conversation.thread_id == thread_id
        ).order_by(
            Conversation.created_at.desc()
        ).limit(limit)
        
        result = await db.execute(stmt)
        messages = list(result.scalars().all())
        messages.reverse()  # Return in chronological order
        
        return messages
