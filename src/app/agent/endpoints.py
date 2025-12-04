"""Agent API endpoints for chat interface."""
import uuid
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.services.user import UserService
from app.services.conversation import ConversationService
from app.agent.graph import create_agent_graph
from app.agent.checkpointer import agent_checkpointer
from app.schemas.chat import ChatRequest, ChatStreamEvent
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/chat")
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Chat with the AI agent (streaming response).
    
    The agent provides role-based assistance for Sales and Pricing teams:
    - Sales: Create opportunities, request quotes, track pipeline
    - Pricing: Create quotes, approve quotes, manage pricing
    """
    try:
        # Get user
        user_service = UserService(db)
        user = await user_service.get_by_id(request.user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Generate or use existing session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"💬 Chat | Session: {session_id[:12]}... | 👤 {user.name} ({user.role.value})")
        
        # Save user message to conversation history
        conv_service = ConversationService(db)
        await conv_service.create_message(
            thread_id=session_id,
            user_id=user.id,
            message_type="human",
            message=request.message
        )
        await db.commit()
        
        # Create agent graph
        graph = await create_agent_graph(
            user_id=user.id,
            user_name=user.name,
            user_role=user.role.value
        )
        
        # Stream response
        async def event_generator() -> AsyncGenerator[str, None]:
            """Generate SSE events for streaming response."""
            try:
                print("\n" + "="*70)
                print(f"🎯 USER INPUT: {request.message}")
                print(f"👤 USER: {user.name} ({user.role.value})")
                print("="*70 + "\n")
                
                final_response = ""
                config = {
                    "configurable": {
                        "thread_id": session_id,
                        "checkpoint_ns": ""
                    }
                }
                
                # Stream events
                async for event in graph.astream_events(
                    {
                        "messages": [{"role": "user", "content": request.message}],
                        "user_id": user.id,
                        "user_name": user.name,
                        "user_role": user.role.value,
                        # Initialize context tracking
                        "current_opportunity_id": None,
                        "current_opportunity_name": None,
                        "current_client_id": None,
                        "current_client_name": None,
                        "current_quote_id": None,
                        "recent_clients": None,
                        "recent_opportunities": None,
                        "recent_products": None,
                        "last_action": None
                    },
                    config=config,
                    version="v2"
                ):
                    event_type = event.get("event")
                    
                    # Handle tool execution events
                    if event_type == "on_tool_start":
                        tool_name = event.get("name", "")
                        tool_input = event.get("data", {}).get("input", {})
                        
                        print(f"\n🔨 TOOL CALLED: {tool_name}")
                        # print(f"📥 TOOL INPUT: {tool_input}")
                        
                        logger.info(f"🔨 Tool: {tool_name}")
                        
                        # Send stage update
                        stage_event = ChatStreamEvent(
                            current_stage=f"⚙️ Executing {tool_name}...",
                            session_id=session_id
                        )
                        yield f"data: {stage_event.model_dump_json()}\n\n"
                    
                    elif event_type == "on_tool_end":
                        tool_name = event.get("name", "")
                        tool_output = event.get("data", {}).get("output", {})
                        
                        print(f"\n✅ TOOL COMPLETED: {tool_name}")
                        # print(f"📤 TOOL OUTPUT: {tool_output}")
                        
                        logger.info(f"✅ Tool Done: {tool_name}")
                        
                        # Send completion update
                        stage_event = ChatStreamEvent(
                            current_stage=f"✅ Completed {tool_name}!",
                            session_id=session_id,
                            tool_output = tool_output
                        )
                        yield f"data: {stage_event.model_dump_json()}\n\n"
                    
                    # Handle chat model streaming
                    elif event_type == "on_chat_model_stream":
                        chunk = event.get("data", {}).get("chunk", {})
                        if hasattr(chunk, "content") and chunk.content:
                            final_response += chunk.content
                
                print("\n" + "="*70)
                print("🤖 FINAL LLM RESPONSE:")
                print(final_response)
                print("="*70 + "\n")
                
                # Save assistant response
                await conv_service.create_message(
                    thread_id=session_id,
                    user_id=user.id,
                    message_type="ai",
                    message=final_response
                )
                await db.commit()
                
                logger.info(f"📤 Response ready ({len(final_response)} chars)")
                
                # Send final message
                final_event = ChatStreamEvent(
                    final_message=final_response,
                    session_id=session_id
                )
                yield f"data: {final_event.model_dump_json()}\n\n"
                
                logger.info(f"✅ Chat complete | Session: {session_id[:12]}...")
                
            except Exception as e:
                logger.error(f"❌ Error in chat stream: {e}")
                import traceback
                traceback.print_exc()
                
                error_event = ChatStreamEvent(
                    error=str(e),
                    session_id=session_id
                )
                yield f"data: {error_event.model_dump_json()}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
