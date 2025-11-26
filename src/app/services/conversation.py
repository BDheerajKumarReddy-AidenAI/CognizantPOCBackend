"""Conversation service for chat history."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.conversation import Conversation
from app.services.base import BaseService
from app.core.logging import get_logger

logger = get_logger(__name__)


class ConversationService(BaseService[Conversation]):
    """Service for conversation/chat history operations."""
    
    async def create_message(
        self,
        thread_id: str,
        user_id: int,
        message_type: str,
        message: str
    ) -> Conversation:
        """Create a new conversation message."""
        try:
            conversation = Conversation(
                thread_id=thread_id,
                user_id=user_id,
                message_type=message_type,
                message=message
            )
            
            self.db.add(conversation)
            await self.db.flush()
            await self.db.refresh(conversation)
            
            return conversation
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ Error creating conversation message: {e}")
            raise
    
    async def get_thread_messages(self, thread_id: str) -> list[Conversation]:
        """Get all messages in a conversation thread."""
        try:
            stmt = (
                select(Conversation)
                .where(
                    Conversation.thread_id == thread_id,
                    # Conversation.user_id == user_id
                )
                .order_by(Conversation.created_at.asc())
            )
            
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"❌ Error getting thread messages: {e}")
            raise
    
    async def get_user_threads(self, user_id: int) -> list[dict]:
        """Get all conversation threads for a user."""
        try:
            # Get first message from each thread
            stmt = (
                select(Conversation)
                .where(Conversation.user_id == user_id)
                .order_by(Conversation.created_at.desc())
            )
            
            result = await self.db.execute(stmt)
            conversations = result.scalars().all()
            
            # Group by thread_id
            threads = {}
            for conv in conversations:
                if conv.thread_id not in threads:
                    threads[conv.thread_id] = {
                        "thread_id": conv.thread_id,
                        "first_message": conv.message,
                        "created_at": conv.created_at
                    }
            
            return list(threads.values())
        except Exception as e:
            logger.error(f"❌ Error getting user threads: {e}")
            raise
