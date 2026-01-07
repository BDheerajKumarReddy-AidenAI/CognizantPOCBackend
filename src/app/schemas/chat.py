"""Chat/Agent schemas."""
from typing import Optional , Any
from pydantic import Field
from app.schemas.base import BaseSchema
from pydantic import BaseModel


class ChatRequest(BaseSchema):
    """Schema for chat requests."""
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = Field(None, alias="thread_id")
    user_id: int = Field(..., description="User ID for conversation tracking")


class ChatStreamEvent(BaseSchema):
    """Schema for streaming chat events."""
    current_stage: Optional[str] = None
    final_message: Optional[str] = None
    error: Optional[str] = None
    tool_output : Optional[Any] = None
    suggestions: Optional[list[str]] = None
    session_id: str = Field(..., alias="thread_id")

class AgentResponse(BaseModel):
    reply: str = Field(
        ...,
        description=(
            "The final user-facing response written in clear, professional markdown. "
            "It must fully reflect and accurately summarize all relevant data available "
            "in the current conversation state and tool outputs. "
            "If a list of items is returned (e.g., accounts, opportunities, quotes, products), "
            "the response must include every item in that list and must not omit, skip, "
            "or selectively summarize entries unless explicitly instructed by the user. "
            "Avoid internal IDs, GUIDs, or technical fields, and present the information "
            "in a clean, readable format (tables or bullet lists). "
            "Highlight important entity names using bold formatting."
        )
    )

    suggestions: list[str] = Field(
        default_factory=list,
        description=(
            "Context-aware follow-up action suggestions based on the current conversation state. "
            "Each suggestion should be a short, actionable phrase (3-8 words) that the user "
            "can click or use as their next query. Examples: 'Update opportunity status', "
            "'View account details', 'Create a quote for this deal'. "
            "Leave empty if no relevant follow-ups exist."
        ),
        max_length=4,
        examples=[
            ["Update opportunity status", "Create quote", "View related contacts"],
            ["Add products to quote", "Convert to sales order"],
            []  # No suggestions when context doesn't warrant them
        ]
        
    )
    class Config:
        json_schema_extra = {
            "example": {
                "reply": "I've successfully created the account **Northwind Traders** in the CRM system.",
                "suggestions": [
                    "Create an opportunity for Northwind",
                    "Add contact person",
                    "View account details"
                ]
            }
        }