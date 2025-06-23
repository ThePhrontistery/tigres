"""
FastAPI API routes for ChatBot IA con Azure OpenAI y contexto del documento funcional.
"""
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
from app.services.openai_service import ask_azure_openai_with_context

router = APIRouter()
templates = Jinja2Templates(directory="templates")
FUNCIONAL_PATH = Path("static/uploads/funcional_generado.md")

@router.get("/chatbot", response_class=HTMLResponse)
def chatbot_page(request: Request):
    """Renderiza la página del chatbot."""
    return templates.TemplateResponse("chatbot/index.html", {"request": request})

@router.post("/chatbot/ask", response_class=JSONResponse)
async def chatbot_ask(question: str = Form(...)) -> dict:
    """Consulta a Azure OpenAI usando el documento funcional como contexto."""
    context = ""
    if FUNCIONAL_PATH.exists():
        context = FUNCIONAL_PATH.read_text(encoding="utf-8")
    answer = await ask_azure_openai_with_context(question, context)
    print(f"[DEBUG] Pregunta: {question}\nRespuesta IA: {answer}")
    return {"answer": answer}
