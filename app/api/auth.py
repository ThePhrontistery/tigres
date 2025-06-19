"""
FastAPI endpoints for authentication (simple demo: user=admin, password=admin).
"""
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND

router = APIRouter()
templates = Jinja2Templates(directory="templates")

USERS = {
    "santiago": "1234",
    "ana": "4567",
    "luz": "7890",
    "admin": "1234",
}

@router.get("/auth/login", response_class=HTMLResponse)
async def login_form(request: Request):
    """Render login form."""
    return templates.TemplateResponse("auth/login.html", {"request": request, "error": None})

@router.post("/auth/login", response_class=HTMLResponse)
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    """Validate login credentials."""
    if username in USERS and password == USERS[username]:
        response = RedirectResponse(url="/", status_code=HTTP_302_FOUND)
        response.set_cookie("session", "dummy-session-token")
        return response
    return templates.TemplateResponse(
        "auth/login.html", {"request": request, "error": "Credenciales incorrectas"}
    )

@router.get("/auth/logout")
async def logout():
    """Cerrar sesión y redirigir a login."""
    response = RedirectResponse(url="/login")
    response.delete_cookie("session")
    return response
