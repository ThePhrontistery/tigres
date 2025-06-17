"""API para procesar Markdown y devolver HTML seguro."""
from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
import markdown as md
from markupsafe import Markup

router = APIRouter(prefix="/api/markdown", tags=["markdown"])

@router.post("/preview", response_class=HTMLResponse)
async def markdown_preview(markdown: str = Form(...)):
    html = md.markdown(markdown, extensions=["extra", "codehilite"])
    # Markup marca el HTML como seguro para Jinja2
    return HTMLResponse(html)