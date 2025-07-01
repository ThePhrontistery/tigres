"""
Main FastAPI app for Metasketch prototype.
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from app.api import documents, content_tree, markdown_editor, chatbot
from app.api.auth import router as auth_router

app = FastAPI(title="Metasketch Prototype")

# Static files (uploads, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Routers
app.include_router(documents.router, prefix="/api")
app.include_router(content_tree.router, prefix="/api")
app.include_router(markdown_editor.router, prefix="/api")
app.include_router(chatbot.router, prefix="/api")
app.include_router(auth_router, prefix="/api")

# CORS (for local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Mostrar pantalla principal solo si el usuario está logueado."""
    session = request.cookies.get("session")
    if session != "dummy-session-token":
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Home"}
    )

@app.get("/login", response_class=HTMLResponse)
async def login_redirect():
    """Redirect /login to /api/auth/login for consistency."""
    return HTMLResponse('<script>window.location.replace("/api/auth/login");</script>')
