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
from langchain_core.messages import ToolMessage
import json
logger = get_logger(__name__)

router = APIRouter()

def extract_json_from_markdown(text: str) -> str:
    """
    Extract JSON from markdown code blocks.
    Handles cases like:
    - ``````
    - ``````
    - Plain JSON: {...}
    """
    # Remove markdown code blocks
    text = text.strip()
    
    # Pattern 1: ``````
    if text.startswith("```"):
        text = text[7:]  # Remove ```json
    # Pattern 2: ``````
    elif text.startswith("```"):
        text = text[3:]  # Remove ```
    
    # Remove trailing ```
    if text.endswith("```"):
        text = text[:-3]
    
    return text.strip()

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
                # pending_tool_output = None
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
                        # tool_name = event.get("name", "")
                        # tool_output = event.get("data", {}).get("output", {})
                        
                        # print(f"\n✅ TOOL COMPLETED: {tool_name}")
                        # # print(f"📤 TOOL OUTPUT: {tool_output}")
                        
                        # logger.info(f"✅ Tool Done: {tool_name}")
                        
                        # # Send completion update
                        # stage_event = ChatStreamEvent(
                        #     current_stage=f"✅ Completed {tool_name}!",
                        #     session_id=session_id,
                        #     tool_output = tool_output
                        # )
                        # yield f"data: {stage_event.model_dump_json()}\n\n"
                        
                        tool_name = event.get("name", "")
                        tool_output = event.get("data", {}).get("output", {})

                        print(f"\n✅ TOOL COMPLETED: {tool_name}")

                        # ---------------------------------------------------------
                        # 🔧 STEP 1 — Normalize tool_output into a Python dict
                        # ---------------------------------------------------------
                        # Case 1: ToolMessage object → use .content
                        if isinstance(tool_output, ToolMessage):
                            tool_output = tool_output.content

                        # Case 2: If it's a JSON string → parse to dict
                        if isinstance(tool_output, str):
                            try:
                                tool_output = json.loads(tool_output)
                            except:
                                # fallback — wrap raw string
                                tool_output = {"raw_output": tool_output}

                        # Case 3: If still not a dict → force convert
                        if not isinstance(tool_output, dict):
                            tool_output = {"raw_output": str(tool_output)}
                        # ---------------------------------------------------------
                        # 🔧 STEP 2 — Inject CRM URL for created Opportunity
                        # ---------------------------------------------------------
                        if tool_name == "create_opportunity" or tool_name == "update_opportunity":
                            opp_id = tool_output.get("opportunityid")
                            if opp_id:
                                crm_url = (
                                    "https://orge47cb78c.crm8.dynamics.com/main.aspx?"
                                    "appid=4c0894ba-19c9-f011-8543-7c1e523cbef1"
                                    "&forceUCI=1&pagetype=entityrecord&etn=opportunity&id="
                                    + str(opp_id)
                                )
                                tool_output["opportunity_crm_url"] = crm_url

                        if tool_name == "create_quote" or tool_name == "update_quote":
                            quote_id = tool_output.get("quoteid")
                            
                            if quote_id:
                                crm_url = (
                                    "https://orge47cb78c.crm8.dynamics.com/main.aspx?"
                                    "appid=4c0894ba-19c9-f011-8543-7c1e523cbef1"
                                    "&forceUCI=1&pagetype=entityrecord&etn=quote&id="
                                    + str(quote_id)
                                )
                                tool_output["quote_crm_url"] = crm_url

                        # if "opportunity_crm_url" in tool_output or "quote_crm_url" in tool_output:
                        #     pending_tool_output = tool_output
                        #     print(f"📌 Buffered tool_output with URL: {pending_tool_output}")
                        # suggestions = []
                        # if tool_name == "get_opportunities":
                        #     suggestions = [
                        #         "View opportunity details",
                        #         "Create a new opportunity",
                        #     ]

                        # elif tool_name == "create_opportunity":
                        #     suggestions = [
                        #         "Create a quote for this opportunity",
                        #     ]

                        

                        # elif tool_name == "create_quote":
                        #     suggestions = [
                        #         "Update this quote with discount",
                        #         "Approve or revise the quote",
                        #     ]

                        # elif tool_name == "create_lead":
                        #     suggestions = [
                        #         "Qualify this lead",
                        #         "Convert the lead to an opportunity",
                        #     ]

                        # ---------------------------------------------------------
                        # 🔧 STEP 3 — Stream updated tool_output to frontend
                        # ---------------------------------------------------------
                        stage_event = ChatStreamEvent(
                            current_stage=f"✅ Completed {tool_name}!",
                            session_id=session_id,
                            tool_output=tool_output,
                            # suggestions=suggestions
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
                ai_reply = ""
                ai_suggestions = []
                
                try:
                    # Extract JSON from markdown code blocks
                    cleaned_response = extract_json_from_markdown(final_response)
                    
                    print(f"🧹 Cleaned response: {cleaned_response[:200]}...")
                    
                    # Try to parse as JSON
                    parsed = json.loads(cleaned_response)
                    ai_reply = parsed.get("reply", final_response)
                    ai_suggestions = parsed.get("suggestions", [])
                    
                    print(f"✅ Parsed successfully!")
                    print(f"📝 Reply length: {len(ai_reply)} chars")
                    print(f"💡 Suggestions: {ai_suggestions}")
                    
                except json.JSONDecodeError as e:
                    # Fallback: use raw response if not valid JSON
                    ai_reply = final_response
                    print(f"⚠️ JSON parse error: {e}")
                    print(f"⚠️ Using raw response as fallback")
                except Exception as e:
                    ai_reply = final_response
                    print(f"⚠️ Unexpected error parsing response: {e}")
                # Save assistant response
                await conv_service.create_message(
                    thread_id=session_id,
                    user_id=user.id,
                    message_type="ai",
                    message=ai_reply
                )
                await db.commit()
                
                logger.info(f"📤 Response ready ({len(ai_reply)} chars, {len(ai_suggestions)} suggestions)")
                
                # Send final message
                final_event = ChatStreamEvent(
                    final_message=ai_reply,
                    session_id=session_id,
                    suggestions=ai_suggestions if ai_suggestions else None
                    # tool_output=pending_tool_output
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
