"""Agent state definition with context tracking."""
from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Enhanced state for the agent graph with comprehensive context tracking.
    
    Context Management Strategy:
    - Track current entities user is working with
    - Remember recent lookups to avoid repeated queries
    - Store conversation intent for better tool selection
    """
    # Core conversation
    messages: Annotated[list, add_messages]
    
    # User context
    user_id: int
    user_name: str
    user_role: str
    
    # Current working context (what user is focused on)
    current_opportunity_id: Optional[int]
    current_opportunity_name: Optional[str]
    current_client_id: Optional[int]
    current_client_name: Optional[str]
    current_quote_id: Optional[int]
    
    # Recently mentioned entities (for reference resolution)
    recent_clients: Optional[list[dict]]
    recent_opportunities: Optional[list[dict]]
    recent_products: Optional[list[dict]]
    
    # Conversation intent tracking
    last_action: Optional[str]
