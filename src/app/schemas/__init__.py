"""Schemas package."""
from app.schemas.base import BaseSchema, SuccessResponse, ErrorResponse
from app.schemas.chat import ChatRequest, ChatStreamEvent
from app.schemas.conversation import (
    ConversationThreadResponse,
    ConversationMessageResponse,
    ConversationMessagesResponse
)
from app.schemas.user import UserResponse, UserCreate, UserListResponse
from app.schemas.client import ClientResponse, ClientCreate, ClientUpdate, ClientListResponse
from app.schemas.contact import ContactResponse, ContactCreate, ContactUpdate, ContactListResponse
from app.schemas.product import ProductResponse, ProductCreate, ProductUpdate, ProductListResponse
from app.schemas.opportunity import (
    OpportunityResponse,
    OpportunityDetailResponse,
    OpportunityCreate,
    OpportunityUpdate,
    OpportunityListResponse,
    QuoteRequest
)
from app.schemas.quote import (
    QuoteResponse,
    QuoteDetailResponse,
    QuoteCreate,
    QuoteUpdate,
    QuoteItemCreate,
    QuoteItemResponse,
    QuoteListResponse
)
from app.schemas.activity import ActivityResponse, ActivityCreate, ActivityListResponse

__all__ = [
    "BaseSchema",
    "SuccessResponse",
    "ErrorResponse",
    "ChatRequest",
    "ChatStreamEvent",
    "ConversationThreadResponse",
    "ConversationMessageResponse",
    "ConversationMessagesResponse",
    "UserResponse",
    "UserCreate",
    "UserListResponse",
    "ClientResponse",
    "ClientCreate",
    "ClientUpdate",
    "ClientListResponse",
    "ContactResponse",
    "ContactCreate",
    "ContactUpdate",
    "ContactListResponse",
    "ProductResponse",
    "ProductCreate",
    "ProductUpdate",
    "ProductListResponse",
    "OpportunityResponse",
    "OpportunityDetailResponse",
    "OpportunityCreate",
    "OpportunityUpdate",
    "OpportunityListResponse",
    "QuoteRequest",
    "QuoteResponse",
    "QuoteDetailResponse",
    "QuoteCreate",
    "QuoteUpdate",
    "QuoteItemCreate",
    "QuoteItemResponse",
    "QuoteListResponse",
    "ActivityResponse",
    "ActivityCreate",
    "ActivityListResponse",
]
