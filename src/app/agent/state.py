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
    current_account_id: Optional[int]
    current_account_name: Optional[str]
    current_quote_id: Optional[int]
    current_quote_name: Optional[str]
    current_sales_order_id: Optional[int]
    current_sales_order_name: Optional[str]
    # Recently mentioned entities (for reference resolution)
    recent_accounts: Optional[list[dict]]
    recent_opportunities: Optional[list[dict]]
    recent_sales_orders: Optional[list[dict]]
    recent_quotes: Optional[list[dict]]
    recent_products: Optional[list[dict]]
    
    # Conversation intent tracking
    last_action: Optional[str]
    
