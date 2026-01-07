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
from app.schemas.chat import ChatRequest, ChatStreamEvent
from app.core.logging import get_logger
from app.config import settings

from langchain_core.messages import ToolMessage
import json

logger = get_logger(__name__)
router = APIRouter()


@router.post("/chat")
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Chat with the AI agent (streaming response).

    Final user-facing response is returned ONLY via `agent_response` tool.
    """
    try:
        # -------------------------------------------------
        # User validation
        # -------------------------------------------------
        user_service = UserService(db)
        user = await user_service.get_by_id(request.user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        session_id = request.session_id or str(uuid.uuid4())

        logger.info(
            f"💬 Chat | Session: {session_id[:12]}... | 👤 {user.name} ({user.role.value})"
        )

        # -------------------------------------------------
        # Persist user message
        # -------------------------------------------------
        conv_service = ConversationService(db)
        await conv_service.create_message(
            thread_id=session_id,
            user_id=user.id,
            message_type="human",
            message=request.message,
        )
        await db.commit()

        # -------------------------------------------------
        # Create agent graph
        # -------------------------------------------------
        graph = await create_agent_graph(
            user_id=user.id,
            user_name=user.name,
            user_role=user.role.value,
        )

        # -------------------------------------------------
        # SSE Event Generator
        # -------------------------------------------------
        async def event_generator() -> AsyncGenerator[str, None]:
            try:
                print("\n" + "=" * 70)
                print(f"🎯 USER INPUT: {request.message}")
                print(f"👤 USER: {user.name} ({user.role.value})")
                print("=" * 70 + "\n")

                ai_reply: str | None = None
                ai_suggestions: list[str] = []

                config = {
                    "configurable": {
                        "thread_id": session_id,
                        "checkpoint_ns": "",
                    }
                }

                async for event in graph.astream_events(
                    {
                        "messages": [{"role": "user", "content": request.message}],
                        "user_id": user.id,
                        "user_name": user.name,
                        "user_role": user.role.value,
                        "current_opportunity_id": None,
                        "current_opportunity_name": None,
                        "current_client_id": None,
                        "current_client_name": None,
                        "current_quote_id": None,
                        "recent_clients": None,
                        "recent_opportunities": None,
                        "recent_products": None,
                        "last_action": None,
                    },
                    config=config,
                    version="v2",
                ):
                    event_type = event.get("event")

                    # ---------------------------------------------
                    # Tool started
                    # ---------------------------------------------
                    if event_type == "on_tool_start":
                        tool_name = event.get("name", "")
                        logger.info(f"🔨 Tool start: {tool_name}")

                        stage_event = ChatStreamEvent(
                            current_stage=f"⚙️ Executing {tool_name}...",
                            session_id=session_id,
                        )
                        yield f"data: {stage_event.model_dump_json()}\n\n"

                    # ---------------------------------------------
                    # Tool finished
                    # ---------------------------------------------
                    elif event_type == "on_tool_end":
                        tool_name = event.get("name", "")
                        tool_output = event.get("data", {}).get("output", {})

                        print(f"\n✅ TOOL COMPLETED: {tool_name}")

                        # Normalize ToolMessage
                        if isinstance(tool_output, ToolMessage):
                            tool_output = tool_output.content

                        if isinstance(tool_output, str):
                            try:
                                tool_output = json.loads(tool_output)
                            except Exception:
                                tool_output = {"raw_output": tool_output}

                        if not isinstance(tool_output, dict):
                            tool_output = {"raw_output": str(tool_output)}

                        # print("Tool Output:", tool_output)
                        # -----------------------------------------
                        # 🎯 FINAL RESPONSE TOOL
                        # -----------------------------------------
                        if tool_name == "agent_response":
                            ai_reply = tool_output.get("reply", "")
                            ai_suggestions = tool_output.get("suggestions", [])

                            print("\n🤖 FINAL STRUCTURED RESPONSE")
                            print(ai_reply)
                            print("💡 Suggestions:", ai_suggestions)

                            # Do NOT stream as stage update
                            continue

                        # -----------------------------------------
                        # CRM URL ENRICHMENT
                        # -----------------------------------------
                        if tool_name in {"create_opportunity", "update_opportunity"}:
                            opp_id = tool_output.get("opportunityid")
                            if opp_id:
                                # tool_output["opportunity_crm_url"] = (
                                #     "https://orgf3531f3f.crm8.dynamics.com/main.aspx"
                                #     "?appid=f90078bf-51c9-f011-8543-000d3af2c247"
                                #     "&pagetype=entityrecord&etn=opportunity&id="
                                #     + str(opp_id)
                                # )
                                tool_output["opportunity_crm_url"] = settings.dynamics.crm_url_entities+"&etn=opportunity&id="+ str(opp_id)
                                tool_output["opportunity_view_all_crm_url"] = settings.dynamics.view_all_crm_url.format(entity="opportunity",view_id=settings.dynamics.opportunity_view_id)

                        if tool_name in {"create_quote", "update_quote","activate_quote","win_quote"}:
                            quote_id = tool_output.get("quoteid")
                            if quote_id:
                                # tool_output["quote_crm_url"] = (
                                #     "https://orgf3531f3f.crm8.dynamics.com/main.aspx"
                                #     "?appid=f90078bf-51c9-f011-8543-000d3af2c247"
                                #     "&pagetype=entityrecord&etn=quote&id="
                                #     + str(quote_id)
                                # )
                                tool_output["quote_crm_url"] = settings.dynamics.crm_url_entities+"&etn=quote&id="+ str(quote_id)
                                tool_output["quote_view_all_crm_url"] = settings.dynamics.view_all_crm_url.format(entity="quote",view_id=settings.dynamics.quote_view_id)

                        if tool_name in {"create_account", "update_account"}:
                            account_id = tool_output.get("accountid")
                            if account_id:
                                # tool_output["account_crm_url"] = (
                                #     "https://orgf3531f3f.crm8.dynamics.com/main.aspx"
                                #     "?appid=f90078bf-51c9-f011-8543-000d3af2c247"
                                #     "&pagetype=entityrecord&etn=account&id="
                                #     + str(account_id)
                                # )
                                tool_output["account_crm_url"] = settings.dynamics.crm_url_entities+"&etn=account&id="+ str(account_id)
                                tool_output["account_view_all_crm_url"] = settings.dynamics.view_all_crm_url.format(entity="account",view_id=settings.dynamics.account_view_id)

                        if tool_name == "convert_quote_to_sales_order":
                            salesorderid = tool_output.get("salesorderid")
                            if salesorderid:
                                # tool_output["salesorder_crm_url"] = (
                                #     "https://orgf3531f3f.crm8.dynamics.com/main.aspx"
                                #     "?appid=f90078bf-51c9-f011-8543-000d3af2c247"
                                #     "&pagetype=entityrecord&etn=salesorder&id="
                                #     + str(salesorderid)
                                # )
                                tool_output["salesorder_crm_url"] = settings.dynamics.crm_url_entities+"&etn=salesorder&id="+ str(salesorderid)
                               
                                tool_output["sales_order_view_all_crm_url"] = settings.dynamics.view_all_crm_url.format(entity="salesorder",view_id=settings.dynamics.salesorder_view_id)
                        

                        stage_event = ChatStreamEvent(
                            current_stage=f"✅ Completed {tool_name}!",
                            session_id=session_id,
                            tool_output=tool_output,
                        )
                        yield f"data: {stage_event.model_dump_json()}\n\n"

                # -------------------------------------------------
                # Persist AI response
                # -------------------------------------------------
                await conv_service.create_message(
                    thread_id=session_id,
                    user_id=user.id,
                    message_type="ai",
                    message=ai_reply or "Could Not reply",
                )
                await db.commit()

                logger.info(
                    f"📤 Response ready ({len(ai_reply or '')} chars, "
                    f"{len(ai_suggestions)} suggestions)"
                )

                final_event = ChatStreamEvent(
                    final_message=ai_reply or "Could not reply.",
                    session_id=session_id,
                    suggestions=ai_suggestions or None,
                )
                yield f"data: {final_event.model_dump_json()}\n\n"

                logger.info(f"✅ Chat complete | Session: {session_id[:12]}...")

            except Exception as e:
                logger.error(f"❌ Error in chat stream: {e}", exc_info=True)
                error_event = ChatStreamEvent(
                    error=str(e),
                    session_id=session_id,
                )
                yield f"data: {error_event.model_dump_json()}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    except Exception as e:
        logger.error(f"❌ Chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
