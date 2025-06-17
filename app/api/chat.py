"""API para chat IA con contexto, system_prompt y user_prompt."""
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import settings
import httpx

router = APIRouter(prefix="/api/chat", tags=["chat"])
templates = Jinja2Templates(directory="templates")

# Simulación de historial en memoria (en producción usar sesión/DB)
chat_history = []

@router.get("/assistant", response_class=HTMLResponse)
async def chat_assistant(request: Request):
    return templates.TemplateResponse("chat_assistant.html", {"request": request, "messages": chat_history[-10:]})

@router.post("/ask", response_class=HTMLResponse)
async def chat_ask(
    request: Request,
    user_prompt: str = Form(...),
    context: str = Form(""),
    system_prompt: str = Form("")
):
    # Añadir mensaje del usuario
    chat_history.append({"role": "user", "content": user_prompt})
    # Llamada simulada al LLM (reemplazar por integración real)
    ai_response = await call_llm(user_prompt, context, system_prompt)
    chat_history.append({"role": "assistant", "content": ai_response})
    return templates.TemplateResponse("chat_assistant.html", {"request": request, "messages": chat_history[-10:]})

async def call_llm(user_prompt: str, context: str, system_prompt: str) -> str:
    api_key = settings.AZURE_OPENAI_API_KEY
    endpoint = settings.AZURE_OPENAI_ENDPOINT
    deployment = settings.AZURE_OPENAI_DEPLOYMENT_NAME
    if not (api_key and endpoint and deployment):
        return "[IA] Configuración de Azure OpenAI incompleta."
    url = f"{endpoint}openai/deployments/{deployment}/chat/completions?api-version=2024-02-15-preview"
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
    }
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if context:
        messages.append({"role": "user", "content": context})
    messages.append({"role": "user", "content": user_prompt})
    data = {
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.95,
        "frequency_penalty": 0,
        "presence_penalty": 0,
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=headers, json=data)
            resp.raise_for_status()
            result = resp.json()
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[IA] Error al consultar el LLM: {e}"
