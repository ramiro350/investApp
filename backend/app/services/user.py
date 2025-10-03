from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.user import UserUpdate
from app.auth.jwt import get_password_hash
from app.auth.jwt import verify_password

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: int):
    """Get user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Get all users with pagination"""
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

async def update_user(db: AsyncSession, user_id: int, user: UserUpdate):
    """Update user information"""
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user.model_dump(exclude_unset=True)
    
    if 'password' in update_data and update_data['password']:
        update_data['password'] = get_password_hash(update_data['password'])
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        password=hashed_password,
        is_active=user.is_active
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, user_id: int):
    """Delete a user"""
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    await db.delete(db_user)
    await db.commit()
    return db_user


async def authenticate_user(db: Session, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        return False
    return user