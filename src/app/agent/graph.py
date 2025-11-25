"""LangGraph agent workflow with state management."""
from typing import Literal
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.types import Command
from app.agent.state import AgentState
from app.agent.tools import get_opportunity_tools
from app.agent.prompts import get_system_prompt
from app.agent.checkpointer import agent_checkpointer
from app.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


def create_agent_graph(user_id: int, user_name: str, user_role: str):
    """Create the agent graph with tools and checkpointer."""
    
    # Get system prompt with user context
    system_prompt = get_system_prompt(user_name, user_role)
    
    print(f"\n{'='*60}")
    print(f"📝 SYSTEM PROMPT (first 300 chars):")
    print(system_prompt[:300] + "...")
    print(f"{'='*60}\n")
    
    # Initialize LLM with API key
    llm = ChatOpenAI(
        model=settings.agent_model,
        temperature=settings.agent_temperature,
        streaming=True,
        api_key=settings.openai_api_key
    )
    
    # Get tools (they manage their own database sessions)
    tools = get_opportunity_tools(user_id)
    llm_with_tools = llm.bind_tools(tools)
    
    # Create base tool node
    base_tool_node = ToolNode(tools)
    
    # Define agent node
    async def agent_node(state: AgentState) -> AgentState:
        """Agent reasoning node with system prompt always included."""
        messages = state["messages"]
        current_opp_id = state.get("current_opportunity_id")
        
        # Build enhanced system prompt with current opportunity context
        enhanced_prompt = system_prompt
        if current_opp_id:
            enhanced_prompt += f"\n\n**CONTEXT**: The user is currently working with opportunity ID {current_opp_id}. If they say 'this opportunity', 'it', or use similar references, they are referring to this opportunity."
        
        # ALWAYS ensure system prompt is at the beginning
        has_system_prompt = (
            len(messages) > 0 and 
            isinstance(messages[0], dict) and 
            messages[0].get("role") == "system"
        )
        
        if not has_system_prompt:
            messages = [{"role": "system", "content": enhanced_prompt}] + messages
            print(f"✅ Added system prompt to messages")
        else:
            messages[0] = {"role": "system", "content": enhanced_prompt}
            print(f"✅ Updated existing system prompt")
        
        if current_opp_id:
            print(f"🎯 Current opportunity context: {current_opp_id}")
        
        print(f"📨 Sending {len(messages)} messages to LLM")
        
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    # Define tools node with state update capability
    async def tools_node_with_state_update(state: AgentState) -> Command:
        """
        Custom tools node that updates current_opportunity_id based on tool calls.
        Returns Command to update state.
        """
        messages = state["messages"]
        last_message = messages[-1] if messages else None
        
        # Track if we need to update current_opportunity_id
        new_opportunity_id = state.get("current_opportunity_id")
        
        # Check if last message has tool calls
        if last_message and hasattr(last_message, "tool_calls"):
            tool_calls = last_message.tool_calls
            
            for tool_call in tool_calls:
                tool_name = tool_call.get("name", "")
                tool_args = tool_call.get("args", {})
                
                print(f"\n🔍 Processing tool: {tool_name}")
                print(f"📥 Tool args: {tool_args}")
                
                # Update current_opportunity_id based on tool interactions
                if tool_name == "create_opportunity":
                    # After creation, we'll get the ID from the tool response
                    print("✨ Will track newly created opportunity")
                
                elif tool_name in ["get_opportunity", "update_opportunity"]:
                    # User is interacting with a specific opportunity
                    if "opp_id" in tool_args:
                        new_opportunity_id = tool_args["opp_id"]
                        print(f"🎯 Setting current opportunity to: {new_opportunity_id}")
                
                elif tool_name == "list_opportunities":
                    # User is browsing, clear current opportunity
                    new_opportunity_id = None
                    print("📋 Cleared current opportunity (listing mode)")
        
        # Execute tools using async invoke
        result = await base_tool_node.ainvoke(state)
        
        # Check tool responses for created opportunity ID
        if result.get("messages"):
            last_tool_message = result["messages"][-1]
            if hasattr(last_tool_message, "content"):
                try:
                    content = last_tool_message.content
                    # Check if this was a create_opportunity response
                    if isinstance(content, str) and "opportunity_id" in content:
                        import json
                        try:
                            parsed = json.loads(content)
                            if parsed.get("opportunity_id"):
                                new_opportunity_id = parsed["opportunity_id"]
                                print(f"✨ Created opportunity ID: {new_opportunity_id}")
                        except:
                            pass
                except Exception as e:
                    print(f"⚠️ Error parsing tool response: {e}")
        
        # Return Command to update state
        print(f"💾 Updating state - current_opportunity_id: {new_opportunity_id}")
        return Command(
            update={
                "messages": result.get("messages", []),
                "current_opportunity_id": new_opportunity_id
            },
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
    
    # Tools node uses Command, so no explicit edge needed
    # The Command in tools_node_with_state_update handles the routing
    
    # Compile with checkpointer
    checkpointer = agent_checkpointer.get()
    graph = workflow.compile(checkpointer=checkpointer)
    
    logger.debug(f"✅ Agent graph compiled | 👤 {user_name} ({user_role})")
    return graph
