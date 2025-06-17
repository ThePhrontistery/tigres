"""Auth API routes: login and token."""
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import authenticate_user, get_db
from app.auth.jwt import create_access_token
from app.models.user import UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user.user})
    return {"access_token": access_token, "token_type": "bearer"}
