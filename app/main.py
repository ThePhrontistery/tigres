"""
Main FastAPI app for Metasketch prototype.
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api import documents, content_tree, markdown_editor, chatbot
from fastapi.templating import Jinja2Templates

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

# CORS (for local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index(request: Request):
    """Simple index page with links to all features."""
    return templates.TemplateResponse(
        "index.html", {"request": request}
    )
