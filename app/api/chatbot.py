"""
FastAPI API routes for ChatBot IA.
"""
from fastapi import APIRouter, Request, HTTPException, Body
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from app.models.chatbot import ChatRequest, ChatResponse
from app.services.openai_service import ask_azure_openai
import asyncio
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/chatbot")
def chatbot_page(request: Request):
    """Render the chatbot page."""
    return templates.TemplateResponse("chatbot/index.html", {"request": request})

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
