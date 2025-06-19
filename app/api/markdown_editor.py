"""
FastAPI API routes for markdown editor.
"""
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/markdown-editor")
def markdown_editor_page(request: Request):
    """Render the markdown editor page."""
    return templates.TemplateResponse("markdown_editor/index.html", {"request": request})
