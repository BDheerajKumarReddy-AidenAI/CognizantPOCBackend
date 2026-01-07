"""LangGraph agent workflow with enhanced state management."""
from typing import Literal
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.types import Command
from app.agent.state import AgentState
from app.agent.tools import get_agent_tools
from app.agent.prompts import get_system_prompt
from app.agent.checkpointer import agent_checkpointer
from app.config import settings
from app.core.logging import get_logger
from langchain_mcp_adapters.client import MultiServerMCPClient
from app.schemas.chat import AgentResponse
from langchain_core.tools import StructuredTool

logger = get_logger(__name__)
tools_require_user_role = {
    "get_opportunities",
    "get_accounts",
    "get_quotes",
    "get_salesorders",
    "create_account",
    "update_account",
    "delete_account",
    "create_opportunity",
    "update_opportunity",
    "delete_opportunity",
    "create_quote",
    "update_quote",
    "delete_quote",
    "create_sales_order",
    "update_sales_order",
    "delete_sales_order",
}

async def create_agent_graph(user_id: int, user_name: str, user_role: str):
    """Create the agent graph with tools and checkpointer."""
    
    # Get system prompt with user context
    system_prompt = get_system_prompt(user_name, user_role)
    
    print(f"\n{'='*60}")
    print(f"📝 SYSTEM PROMPT (first 500 chars):")
    print(system_prompt[:500] + "...")
    print(f"{'='*60}\n")
    
    # Initialize LLM
    llm = ChatOpenAI(
        model=settings.agent.model,
        temperature=settings.agent.temperature,
        streaming=True,
        api_key=settings.openai.api_key
    )
    # ------------------------------
    # Final response tool (STRICT)
    # ------------------------------
    agent_response_tool = StructuredTool.from_function(
        name="agent_response",
        description="Final structured response to the user",
        args_schema=AgentResponse,
        func=lambda **kwargs: kwargs,
    )
    
    # Get tools based on user role
    # from app.db.models.user import UserRole
    # tools = get_agent_tools(user_id, UserRole(user_role))
    # llm_with_tools = llm.bind_tools(tools)
    
    # # Create base tool node
    # base_tool_node = ToolNode(tools)


    # Load MCP tools instead of internal tools


    print("🔌 Connecting to Dynamics MCP server...")

    if settings.mcp.enabled:
        client = MultiServerMCPClient({
            "dynamics": {
                "url": settings.mcp.url,
                "transport": settings.mcp.transport
            }
        })
    else:
        raise ValueError("MCP is not enabled in settings.")

    mcp_tools = await client.get_tools()

    print(f"🔧 Loaded {len(mcp_tools)} Dynamics MCP tools")

    # Bind tools (MCP + final response)
    llm_with_tools = llm.bind_tools(
        mcp_tools + [agent_response_tool],
        tool_choice="auto",
    )

    base_tool_node = ToolNode(mcp_tools + [agent_response_tool])

    
    # Define agent node
    async def agent_node(state: AgentState) -> AgentState:
        """Agent reasoning node with context-aware system prompt."""
        messages = state["messages"]
        
        # Build context-aware system prompt
        context_additions = []
        
        if state.get("current_opportunity_id"):
            context_additions.append(
                f"📌 Current Context: Working on opportunity '{state.get('current_opportunity_name')}' "
                f"(ID: {state.get('current_opportunity_id')}) "
                f"for client '{state.get('current_account_name')}'"
            )
        
        if state.get("recent_opportunities"):
            recent = state["recent_opportunities"][:10]
            opp_list = ", ".join([f"'{o['name']}'" for o in recent])
            context_additions.append(
                f"📋 Recently Listed: {opp_list}"
            )
        
        if state.get('recent_quotes'):
            recent = state['recent_quotes'][:10]
            quote_list = ", ".join([f"'{q['quote_number']}'" for q in recent])
            context_additions.append(
                f"📄 Recently Listed Quotes: {quote_list}"
            )

        if state.get("recent_accounts"):
            recent = state["recent_accounts"][:10]
            acc_list = ", ".join([f"'{a['name']}'" for a in recent])
            context_additions.append(
                f"🏢 Recently Listed Accounts: {acc_list}"
            )
        if state.get("recent_products"):
            recent = state["recent_products"][:10]
            prod_list = ", ".join([f"'{p['name']}'" for p in recent])
            context_additions.append(
                f"📦 Recently Listed Products: {prod_list}"
            )
        if state.get("recent_salesorders"):
            recent = state["recent_salesorders"][:10]
            so_list = ", ".join([f"'{s['name']}'" for s in recent])
            context_additions.append(
                f"🧾 Recently Listed Sales Orders: {so_list}"
            )
            
        if state.get("last_action"):
            context_additions.append(
                f"🔄 Last Action: {state['last_action']}"
            )
        
        enhanced_prompt = system_prompt
        if context_additions:
            enhanced_prompt += "\n\n### CURRENT CONVERSATION CONTEXT:\n"
            enhanced_prompt += "\n".join(context_additions)
            enhanced_prompt += "\n\nUse this context to understand user references like 'it', 'that opportunity', 'the deal', etc."
        
        # ALWAYS ensure system prompt is at the beginning
        has_system_prompt = (
            len(messages) > 0 and 
            isinstance(messages[0], dict) and 
            messages[0].get("role") == "system"
        )
        
        if not has_system_prompt:
            messages = [{"role": "system", "content": enhanced_prompt}] + messages
            print(f"✅ Added system prompt with context")
        else:
            messages[0] = {"role": "system", "content": enhanced_prompt}
            print(f"✅ Updated system prompt with context")
        
        if state.get("current_opportunity_id"):
            print(f"🎯 Context: Opportunity #{state['current_opportunity_id']} - {state.get('current_opportunity_name')}")
        
        print(f"📨 Sending {len(messages)} messages to LLM")
        
        response = llm_with_tools.invoke(messages)
        # 🔐 SAFETY: if model returns no tool calls, force agent_response
        if not getattr(response, "tool_calls", None):
            response = llm_with_tools.invoke(
                messages + [{
                    "role": "system",
                    "content": "You must now call agent_response."
                }]
            )
        return {"messages": [response]}
    
    # Define tools node with state update capability
    async def tools_node_with_state_update(state: AgentState) -> Command:
        """
        Custom tools node that updates state based on tool results.
        Tracks current entities and recent lookups for context.
        """
        messages = state["messages"]
        last_message = messages[-1] if messages else None
        
        # Initialize state updates
        state_updates = {}
        
        # Check if last message has tool calls
        if last_message and hasattr(last_message, "tool_calls"):
            tool_calls = last_message.tool_calls
            for tool_call in tool_calls:
                tool_name = tool_call.get("name", "")
                tool_args = tool_call.get("args", {})
                if tool_name in tools_require_user_role and isinstance(tool_args, dict):
                    tool_args["user_role"] = state["user_role"]
                    tool_call["args"] = tool_args

        
        # Execute tools
        result = await base_tool_node.ainvoke(state)
        
        # Parse tool results and update state
        if result.get("messages"):
            for tool_message in result["messages"]:
                if hasattr(tool_message, "content"):
                    try:
                        import json
                        content = tool_message.content
                        if isinstance(content, str) and content.strip().startswith("{"):
                            parsed = json.loads(content)
                            
                            # Update state based on tool results
                            
                           
                            
                            # 1. Track listed opportunities
                            if "opportunities" in parsed and isinstance(parsed["opportunities"], list):
                                recent_opps = [
                                    {
                                        "id": opp.get("opportunityid"),
                                        "name": opp.get("name"),
                                        # "client_name": opp.get("client_name")
                                    }
                                    for opp in parsed["opportunities"]
                                ]
                                state_updates["recent_opportunities"] = recent_opps
                                state_updates["last_action"] = "listed_opportunities"
                        
                                print(f"📋 Cached {len(recent_opps)} recent opportunities")
                                # print("State updates:",state_updates)
                            
                            # 2. Track listed accounts
                            if "accounts" in parsed and isinstance(parsed["accounts"], list):
                                recent_accounts = [
                                    {
                                     "accountid": c.get("accountid"),
                                      "name": c.get("name")
                                    }
                                    for c in parsed["accounts"]
                                ]
                                state_updates["recent_accounts"] = recent_accounts
                                state_updates["last_action"] = "listed_accounts"
                                # print(parsed)
                                print(f"🏢 Cached {len(recent_accounts)} Recent Accounts {state_updates}")


                             # 6. Track listed quotes
                            if "quotes" in parsed and isinstance(parsed["quotes"], list):
                                recent_quotes = [
                                    {
                                        "id": quote.get("quoteid"),
                                        "name": quote.get("name"),
                                        "quote_number": quote.get("quotenumber"),
                                        "opportunity_id": quote.get("_opportunityid_value"),
                                        "account_id": quote.get("_accountid_value")
                                    }
                                    for quote in parsed["quotes"]
                                ]
                                state_updates["recent_quotes"] = recent_quotes
                                state_updates["last_action"] = "listed_quotes"
                                print(f"📋 Cached {len(recent_quotes)} recent quotes")
                            
                            # 3. Track listed products
                            if "products" in parsed and isinstance(parsed["products"], list):
                                recent_products = [
                                    {
                                        "id": p.get("id"),
                                        "name": p.get("name"),
                                        "price": p.get("unit_price")
                                    }
                                    for p in parsed["products"][:10]
                                ]
                                state_updates["recent_products"] = recent_products
                                state_updates["last_action"] = "listed_products"
                                print(f"📦 Cached {len(recent_products)} products")
                            
                            
                            odata_context = parsed.get("@odata.context", "")
                             # 4. Track created/viewed opportunity (SAFE)
                            if "#opportunities" in odata_context and "opportunityid" in parsed:
                                state_updates["current_opportunity_id"] = parsed.get("opportunityid")
                                state_updates["current_opportunity_name"] = parsed.get("name")

                                # Optional related context
                                if parsed.get("_accountid_value"):
                                    state_updates["current_account_id"] = parsed.get("_accountid_value")

                                if parsed.get("account_name"):
                                    state_updates["current_account_name"] = parsed.get("account_name")

                                print(
                                    f"🎯 Updated context: Opportunity "
                                    f"'{parsed.get('name', 'Unknown')}'"
                                )

                            # 5. Create a quote
                            if "#quotes" in odata_context and "quoteid" in parsed:
                                state_updates["current_quote_id"] = parsed.get("quoteid")
                                state_updates["current_quote_number"] = parsed.get("quotenumber")
                                state_updates["last_action"] = "created_quote"

                                # Optional relational context
                                if parsed.get("_opportunityid_value"):
                                    state_updates["current_opportunity_id"] = parsed.get("_opportunityid_value")

                                if parsed.get("_accountid_value"):
                                    state_updates["current_account_id"] = parsed.get("_accountid_value")

                                print(
                                    f"💰 Created quote "
                                    f"{parsed.get('quotenumber', 'Unknown')}"
                                )
                            
                            # 6. Create a sales order
                            if "#salesorders" in odata_context and "salesorderid" in parsed:
                                state_updates["current_salesorder_id"] = parsed.get("salesorderid")
                                state_updates["current_salesorder_name"] = parsed.get("name")
                                state_updates["current_salesorder_number"] = parsed.get("ordernumber")
                                state_updates["last_action"] = "created_salesorder"
                              
                                # Optional relational context
                                if parsed.get("_opportunityid_value"):
                                    state_updates["current_opportunity_id"] = parsed.get("_opportunityid_value")

                                if parsed.get("_quoteid_value"):
                                    state_updates["current_quote_id"] = parsed.get("_quoteid_value")

                                if parsed.get("_customerid_value"):
                                    state_updates["current_customer_id"] = parsed.get("_customerid_value")

                                if parsed.get("_accountid_value"):
                                    state_updates["current_account_id"] = parsed.get("_accountid_value")

                                print(
                                    f"🧾 Created Sales Order "
                                    f"{parsed.get('ordernumber', 'Unknown')}"
                                )

                           

                    except json.JSONDecodeError:
                        pass
                    except Exception as e:
                        print(f"⚠️ Error parsing tool result: {e}")
        
        # Merge state updates
        final_updates = {
            "messages": result.get("messages", []),
            **state_updates
        }
        
        print(f"💾 State updates: {list(state_updates.keys())}")
        
        has_agent_response = any(
            getattr(msg, "name", "") == "agent_response"
            for msg in result.get("messages", [])
        )

        return Command(
            update=final_updates,
            goto="end" if has_agent_response else "agent"
        )
    
    # ---------------------------------------------------------
    # Router
    # ---------------------------------------------------------
    def should_continue(state: AgentState):
        last = state["messages"][-1]
        if getattr(last, "tool_calls", None):
            return "tools"
        return "end"


    # Build graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tools_node_with_state_update)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    
    # Compile with checkpointer
    checkpointer = agent_checkpointer.get()
    graph = workflow.compile(checkpointer=checkpointer)
    
    logger.debug(f"✅ Agent graph compiled | 👤 {user_name} ({user_role})")
    return graph
