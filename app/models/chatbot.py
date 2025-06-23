from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    """Modelo para la petición al chatbot."""
    message: str
    document_content: Optional[str] = None

class ChatResponse(BaseModel):
    """Modelo para la respuesta del chatbot."""
    response: str
