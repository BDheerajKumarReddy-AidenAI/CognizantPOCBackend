"""Database models package."""
from app.db.models.user import User, UserRole
from app.db.models.client import Client, ClientStatus
from app.db.models.contact import Contact
from app.db.models.product import Product
from app.db.models.opportunity import Opportunity, OpportunityStage
from app.db.models.quote import Quote, QuoteStatus
from app.db.models.quote_item import QuoteItem
from app.db.models.activity import Activity, ActivityType
from app.db.models.conversation import Conversation

__all__ = [
    "User",
    "UserRole",
    "Client",
    "ClientStatus",
    "Contact",
    "Product",
    "Opportunity",
    "OpportunityStage",
    "Quote",
    "QuoteStatus",
    "QuoteItem",
    "Activity",
    "ActivityType",
    "Conversation",
]
