"""User API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from sqlalchemy import select, or_
from app.services.user import UserService
from app.db.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserListResponse

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user."""
    service = UserService(db)
    
    # Check if email already exists
    existing = await service.get_by_email(data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = await service.create(data)
    await db.commit()
    return user


@router.get("/", response_model=UserListResponse)
async def list_users(db: AsyncSession = Depends(get_db)):
    """List all users."""
    service = UserService(db)
    users = await service.list()
    return {"users": users, "total": len(users)}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a user by ID."""
    service = UserService(db)
    user = await service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

# @router.get("/by-name/{user_name}", response_model=UserResponse)
# async def get_user_by_name(user_name: str, db: AsyncSession = Depends(get_db)):
#     """Get user by name."""
#     result = await db.execute(select(User).where(User.name == user_name))
#     user = result.scalar_one_or_none()
    
#     if not user:
#         from fastapi import HTTPException
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

@router.get("/by-name/{identifier}", response_model=UserResponse)
async def get_user_by_identifier(
    identifier: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by name or email.
    
    The identifier can be either:
    - User's name (e.g., "John Sales")
    - User's email (e.g., "john@company.com")
    
    This endpoint searches both fields.
    """
    # Search for user by name OR email
    stmt = select(User).where(
        or_(
            User.name == identifier,
            User.email == identifier
        )
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found with identifier: {identifier}"
        )
    
    return user