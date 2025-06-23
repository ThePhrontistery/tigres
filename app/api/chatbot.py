"""
FastAPI API routes for ChatBot IA con Azure OpenAI y contexto del documento funcional.
"""
<<<<<<< HEAD
from fastapi import APIRouter, Request, HTTPException, Body
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from app.models.chatbot import ChatRequest, ChatResponse
from app.services.openai_service import ask_azure_openai
import asyncio
from typing import Optional
=======
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
from app.services.openai_service import ask_azure_openai_with_context
>>>>>>> 63fc833c99224178f72546ed75dd2efafa9cfe35

router = APIRouter()
templates = Jinja2Templates(directory="templates")
FUNCIONAL_PATH = Path("static/uploads/funcional_generado.md")

@router.get("/chatbot", response_class=HTMLResponse)
def chatbot_page(request: Request):
    """Renderiza la página del chatbot."""
    return templates.TemplateResponse("chatbot/index.html", {"request": request})

<<<<<<< HEAD
@router.post("/chatbot", response_model=ChatResponse)
async def chatbot_ask(
    data: ChatRequest = Body(...)
):
    """Recibe mensaje y contexto, responde usando Azure OpenAI."""
    if not data.message:
        raise HTTPException(status_code=400, detail="Falta el mensaje para la consulta.")
    # document_content puede ser vacío
    try:
        response = await ask_azure_openai(data.message, data.document_content or "")
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error IA: {str(e)}")
=======
@router.post("/chatbot/ask", response_class=JSONResponse)
async def chatbot_ask(question: str = Form(...)) -> dict:
    """Consulta a Azure OpenAI usando el documento funcional como contexto."""
    context = ""
    if FUNCIONAL_PATH.exists():
        context = FUNCIONAL_PATH.read_text(encoding="utf-8")
    answer = await ask_azure_openai_with_context(question, context)
    print(f"[DEBUG] Pregunta: {question}\nRespuesta IA: {answer}")
    return {"answer": answer}
>>>>>>> 63fc833c99224178f72546ed75dd2efafa9cfe35
