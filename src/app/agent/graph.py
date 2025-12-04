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


logger = get_logger(__name__)


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
        model=settings.agent_model,
        temperature=settings.agent_temperature,
        streaming=True,
        api_key=settings.openai_api_key
    )
    
    # Get tools based on user role
    # from app.db.models.user import UserRole
    # tools = get_agent_tools(user_id, UserRole(user_role))
    # llm_with_tools = llm.bind_tools(tools)
    
    # # Create base tool node
    # base_tool_node = ToolNode(tools)


    # Load MCP tools instead of internal tools


    print("🔌 Connecting to Dynamics MCP server...")

    client = MultiServerMCPClient({
        "dynamics": {
            "url": "http://127.0.0.1:6000/mcp",
            "transport": "streamable_http"
        }
    })

    mcp_tools = await client.get_tools()

    print(f"🔧 Loaded {len(mcp_tools)} Dynamics MCP tools")

    llm_with_tools = llm.bind_tools(mcp_tools)

    base_tool_node = ToolNode(mcp_tools)

    
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
                f"for client '{state.get('current_client_name')}'"
            )
        
        if state.get("recent_opportunities"):
            recent = state["recent_opportunities"][:3]
            opp_list = ", ".join([f"'{o['name']}'" for o in recent])
            context_additions.append(
                f"📋 Recently Listed: {opp_list}"
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
                
                print(f"\n🔍 Processing tool: {tool_name}")
                print(f"📥 Tool args: {tool_args}")
        
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
                            
                            # 1. Track created/viewed opportunity
                            if "opportunity_id" in parsed and "opportunity_name" in parsed:
                                state_updates["current_opportunity_id"] = parsed["opportunity_id"]
                                state_updates["current_opportunity_name"] = parsed["opportunity_name"]
                                if "client_id" in parsed:
                                    state_updates["current_client_id"] = parsed["client_id"]
                                if "client_name" in parsed:
                                    state_updates["current_client_name"] = parsed["client_name"]
                                print(f"🎯 Updated context: Opportunity '{parsed['opportunity_name']}'")
                            
                            # 2. Track listed opportunities
                            if "opportunities" in parsed and isinstance(parsed["opportunities"], list):
                                recent_opps = [
                                    {
                                        "id": opp.get("id"),
                                        "name": opp.get("name"),
                                        "client_name": opp.get("client_name")
                                    }
                                    for opp in parsed["opportunities"][:5]
                                ]
                                state_updates["recent_opportunities"] = recent_opps
                                state_updates["last_action"] = "listed_opportunities"
                                print(f"📋 Cached {len(recent_opps)} recent opportunities")
                            
                            # 3. Track listed clients
                            if "clients" in parsed and isinstance(parsed["clients"], list):
                                recent_clients = [
                                    {"id": c.get("id"), "name": c.get("name")}
                                    for c in parsed["clients"][:10]
                                ]
                                state_updates["recent_clients"] = recent_clients
                                state_updates["last_action"] = "listed_clients"
                                print(f"🏢 Cached {len(recent_clients)} clients")
                            
                            # 4. Track listed products
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
                            
                            # 5. Track created quote
                            if "quote_id" in parsed and "quote_number" in parsed:
                                state_updates["current_quote_id"] = parsed["quote_id"]
                                state_updates["last_action"] = "created_quote"
                                print(f"💰 Created quote {parsed['quote_number']}")
                            
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
        
        return Command(
            update=final_updates,
            goto="agent"
        )
    
    # Router function to decide next step
    def should_continue(state: AgentState) -> Literal["tools", "end"]:
        """Determine if we should continue to tools or end."""
        messages = state["messages"]
        last_message = messages[-1] if messages else None
        
        # Check if there are tool calls
        if last_message and hasattr(last_message, "tool_calls") and last_message.tool_calls:
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
