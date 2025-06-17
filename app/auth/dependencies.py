"""OAuth2 and authentication dependencies."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError
from collections.abc import AsyncGenerator
from app.db.session import SessionLocal
from app.models.user import UserORM
from app.utils.hashing import verify_password
from app.auth.jwt import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

async def authenticate_user(db: AsyncSession, username: str, password: str) -> UserORM | None:
    result = await db.execute(select(UserORM).where(UserORM.user == username))
    user = result.scalar_one_or_none()
    if user and verify_password(password, user.password):
        return user
    return None

def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
