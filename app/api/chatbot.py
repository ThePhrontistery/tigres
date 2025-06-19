"""
FastAPI API routes for ChatBot IA.
"""
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/chatbot")
def chatbot_page(request: Request):
    """Render the chatbot page."""
    return templates.TemplateResponse("chatbot/index.html", {"request": request})
