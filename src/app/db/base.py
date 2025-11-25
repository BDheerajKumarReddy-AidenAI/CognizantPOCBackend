"""
Import all models here for Alembic to detect them.
This file must be imported in alembic/env.py.
"""
from app.core.database import Base

# Import associations first
from app.db.models.associations import opportunity_product

# Import models in dependency order
from app.db.models.user import User
from app.db.models.client import Client
from app.db.models.product import Product
from app.db.models.opportunity import Opportunity
from app.db.models.conversation import Conversation

__all__ = [
    "Base",
    "User",
    "Client",
    "Product",
    "Opportunity",
    "Conversation",
    "opportunity_product"
]
