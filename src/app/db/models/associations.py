"""Association tables for many-to-many relationships."""
from sqlalchemy import Column, ForeignKey, Table
from app.core.database import Base


opportunity_product = Table(
    "opportunity_product",
    Base.metadata,
    Column("opportunity_id", ForeignKey("opportunities.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True)
)
