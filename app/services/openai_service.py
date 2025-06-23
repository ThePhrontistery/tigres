"""
Servicio para generación de análisis funcional usando Azure OpenAI.
"""
from typing import List
import os
import openai
from openai import AzureOpenAI
from docx import Document
from PyPDF2 import PdfReader
import asyncio

def extract_text_from_file(file_path: str) -> str:
    """Extrae texto de un archivo PDF, DOCX o TXT."""
    if file_path.lower().endswith(".pdf"):
        try:
            reader = PdfReader(file_path)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            return f"[No se pudo extraer texto del PDF: {os.path.basename(file_path)}]"
    elif file_path.lower().endswith(".docx"):
        try:
            doc = Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            return f"[No se pudo extraer texto del DOCX: {os.path.basename(file_path)}]"
    else:
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return f"[No se pudo leer el archivo: {os.path.basename(file_path)}]"

def generate_funcional_analysis(file_paths: List[str]) -> str:
    """Genera un análisis funcional usando Azure OpenAI a partir de los documentos subidos."""
    docs_content = []
    for path in file_paths:
        # Ignorar el archivo funcional generado para evitar recursividad
        if os.path.basename(path) == "funcional_generado.md":
            continue
        content = extract_text_from_file(path)
        docs_content.append(f"# {os.path.basename(path)}\n\n{content}")
    if not docs_content:
        return "[No se pudo extraer texto de ningún documento válido.]"
    prompt = (
        "Eres un analista funcional experto. Resume y sintetiza los siguientes documentos en un único análisis funcional claro y estructurado en formato Markdown.\n\n" + "\n\n".join(docs_content)
    )
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2023-05-15",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": "Eres un analista funcional experto."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=2048,
    )
    return response.choices[0].message.content

async def ask_azure_openai(message: str, document_content: str) -> str:
    """Consulta Azure OpenAI con o sin contexto de documento funcional."""
    if document_content.strip():
        prompt = (
            "Eres un asistente experto en análisis funcional. Responde la consulta del usuario usando únicamente la información relevante del siguiente documento funcional en Markdown.\n\n"
            f"DOCUMENTO FUNCIONAL:\n{document_content}\n\n"
            f"PREGUNTA DEL USUARIO: {message}"
        )
    else:
        prompt = (
            "Eres un asistente de IA. Responde la consulta del usuario de forma clara y útil.\n\n"
            f"PREGUNTA DEL USUARIO: {message}"
        )
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2023-05-15",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )
    response = await asyncio.to_thread(
        client.chat.completions.create,
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": "Eres un asistente de IA experto."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=1024,
    )
    return response.choices[0].message.content
