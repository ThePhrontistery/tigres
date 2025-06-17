"""API para servir el editor markdown como fragmento para HTMX."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/markdown/editor", response_class=HTMLResponse)
async def markdown_editor(request: Request):
    return templates.TemplateResponse("markdown_editor.html", {"request": request})
