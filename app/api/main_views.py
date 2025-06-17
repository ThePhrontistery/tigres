"""Main HTML views: login and metasketch dashboard."""
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import authenticate_user, get_db
from app.auth.jwt import create_access_token

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login", response_class=HTMLResponse)
async def login_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Credenciales incorrectas"})
    access_token = create_access_token({"sub": user.user})
    response = RedirectResponse(url="/metasketch", status_code=302)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@router.get("/metasketch", response_class=HTMLResponse)
async def metasketch_dashboard(request: Request):
    return templates.TemplateResponse("metasketch.html", {"request": request})
