"""LangGraph agent workflow."""
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from app.agent.state import AgentState
from app.agent.tools import get_opportunity_tools
from app.agent.prompts import get_system_prompt
from app.agent.checkpointer import agent_checkpointer
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def create_agent_graph(user_id: int, user_name: str, user_role: str):
    """Create the agent graph with tools and checkpointer."""
    
    # Initialize LLM with API key from settings
    llm = ChatOpenAI(
        model=settings.agent_model,
        temperature=settings.agent_temperature,
        streaming=True,
        api_key=settings.openai_api_key
    )
    
    # Get tools (they manage their own database sessions)
    tools = get_opportunity_tools(user_id)
    llm_with_tools = llm.bind_tools(tools)
    
    # Get system prompt with user context
    system_prompt = get_system_prompt(user_name, user_role)
    
    # Define agent node
    def agent_node(state: AgentState) -> AgentState:
        """Agent reasoning node."""
        messages = state["messages"]
        
        # Add system prompt if first message
        if len(messages) == 1:
            system_message = {"role": "system", "content": system_prompt}
            messages = [system_message] + messages
        
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    # Build graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "tools",
            END: END
        }
    )
    
    # After tools, go back to agent
    workflow.add_edge("tools", "agent")
    
    # Compile with checkpointer
    checkpointer = agent_checkpointer.get()
    graph = workflow.compile(checkpointer=checkpointer)
    
    logger.debug(f"Agent graph compiled for user: {user_name} ({user_role})")
    return graph
