"""
FastAPI API routes for content tree.
"""
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/content-tree")
def content_tree_page(request: Request):
    """Render the content tree page."""
    return templates.TemplateResponse("content_tree/index.html", {"request": request})
