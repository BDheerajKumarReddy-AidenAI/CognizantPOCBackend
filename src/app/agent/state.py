"""Agent state definition."""
from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State for the agent graph with user context and current opportunity tracking."""
    messages: Annotated[list, add_messages]
    user_id: int
    user_name: str
    user_role: str
    current_opportunity_id: Optional[int]  # Track the currently focused opportunity
