"""API v1 router."""
from fastapi import APIRouter
from app.api.v1 import users, clients, products, opportunities, quotes, conversations

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(opportunities.router, prefix="/opportunities", tags=["opportunities"])
api_router.include_router(quotes.router, prefix="/quotes", tags=["quotes"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
