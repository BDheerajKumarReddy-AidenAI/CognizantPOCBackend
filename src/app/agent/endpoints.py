"""Agent chat endpoints."""
import uuid
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.chat import ChatRequest
from app.db.session import get_db
from app.db.models.user import User
from app.agent.graph import create_agent_graph
from app.agent.history import ConversationHistory
from app.agent.streaming import get_friendly_tool_message, format_sse_event
from app.core.database import AsyncSessionLocal
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="", tags=["Agent"])


@router.post("/chat")
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Streaming chat endpoint with SSE."""
    session_id = request.session_id or str(uuid.uuid4())
    
    # Fetch user information
    result = await db.execute(select(User).where(User.id == request.user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User {request.user_id} not found")
    
    logger.info(f"💬 Chat | Session: {session_id[:8]}... | 👤 {user.name} ({user.role.value})")
    
    # Save user message
    try:
        await ConversationHistory.save_message(
            db=db,
            thread_id=session_id,
            user_id=request.user_id,
            message=request.message,
            message_type="human"
        )
        await db.commit()
    except Exception as e:
        logger.error(f"Error saving user message: {e}")
        await db.rollback()
    
    async def event_stream():
        try:
            # Create agent graph with user context
            graph = create_agent_graph(
                user_id=user.id,
                user_name=user.name,
                user_role=user.role.value
            )
            config = {"configurable": {"thread_id": session_id}}
            
            print(f"\n{'='*60}")
            print(f"🎯 USER INPUT: {request.message}")
            print(f"👤 USER: {user.name} ({user.role.value})")
            print(f"{'='*60}\n")
            
            # Track tool executions
            tool_executions = {}
            final_content = ""
            
            # Stream events
            async for event in graph.astream_events(
                {
                    "messages": [{"role": "user", "content": request.message}],
                    "user_id": user.id,
                    "user_name": user.name,
                    "user_role": user.role.value,
                    "current_opportunity_id": None
                },
                config=config,
                version="v2"
            ):
                kind = event["event"]
                
                # Tool execution started
                if kind == "on_tool_start":
                    tool_name = event.get("name", "")
                    tool_input = event.get("data", {}).get("input", {})
                    run_id = event.get("run_id", "")
                    
                    print(f"\n🔨 TOOL CALLED: {tool_name}")
                    print(f"📥 TOOL INPUT: {tool_input}\n")
                    
                    logger.info(f"🔨 Tool: {tool_name}")
                    
                    tool_executions[run_id] = {
                        "name": tool_name,
                        "args": tool_input
                    }
                    
                    start_message = get_friendly_tool_message(
                        tool_name,
                        tool_input,
                        stage="start"
                    )
                    
                    yield await format_sse_event({
                        "current_stage": start_message,
                        "session_id": session_id
                    })
                    await asyncio.sleep(0)
                
                # Tool execution completed
                elif kind == "on_tool_end":
                    tool_name = event.get("name", "")
                    tool_output = event.get("data", {}).get("output", "")
                    run_id = event.get("run_id", "")
                    
                    print(f"\n✅ TOOL COMPLETED: {tool_name}")
                    print(f"📤 TOOL OUTPUT: {tool_output}\n")
                    
                    logger.info(f"✅ Tool Done: {tool_name}")
                    
                    tool_info = tool_executions.get(run_id, {"name": tool_name, "args": {}})
                    complete_message = get_friendly_tool_message(
                        tool_name,
                        tool_info["args"],
                        stage="complete"
                    )
                    
                    yield await format_sse_event({
                        "current_stage": complete_message,
                        "session_id": session_id
                    })
                    await asyncio.sleep(0)
                
                # Capture final content from model
                elif kind == "on_chat_model_stream":
                    data = event.get("data", {})
                    chunk = data.get("chunk")
                    
                    if chunk:
                        content = getattr(chunk, "content", None) or (
                            chunk.get("content") if isinstance(chunk, dict) else None
                        )
                        if content:
                            final_content += content
            
            print(f"\n{'='*60}")
            print(f"🤖 FINAL LLM RESPONSE:")
            print(final_content)
            print(f"{'='*60}\n")
            
            # Send final message and save to history
            if final_content:
                logger.info(f"📤 Response ready ({len(final_content)} chars)")
                
                # Save AI message with a fresh session
                try:
                    async with AsyncSessionLocal() as save_db:
                        await ConversationHistory.save_message(
                            db=save_db,
                            thread_id=session_id,
                            user_id=request.user_id,
                            message=final_content,
                            message_type="ai"
                        )
                        await save_db.commit()
                except Exception as e:
                    logger.error(f"Error saving AI message: {e}")
                
                yield await format_sse_event({
                    "final_message": final_content,
                    "session_id": session_id
                })
            
            logger.info(f"✅ Chat complete | Session: {session_id[:8]}...")
            
        except Exception as e:
            logger.error(f"❌ Chat error: {str(e)}", exc_info=True)
            yield await format_sse_event({
                "error": f"Error: {str(e)}",
                "session_id": session_id
            })
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/health")
async def agent_health():
    """Agent health check."""
    return {"status": "healthy", "service": "agent"}
