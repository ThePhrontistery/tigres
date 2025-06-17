"""API y vistas parciales para gestión de documentos."""
from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import status
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/documents/upload-modal", response_class=HTMLResponse)
async def show_upload_modal(request: Request):
    # Leer categorías desde el fichero categories.txt
    categories = []
    try:
        with open("categories.txt", encoding="utf-8") as f:
            categories = [line.strip() for line in f if line.strip()]
    except Exception:
        categories = []
    return templates.TemplateResponse("documents_upload.html", {"request": request, "categories": categories})

@router.get("/documents/close-modal", response_class=HTMLResponse)
async def close_modal(request: Request):
    # Devuelve un div vacío para cerrar el modal
    return HTMLResponse("")

@router.post("/api/documents/upload", response_class=HTMLResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_documents(
    request: Request,
    files: list[UploadFile] = File(...),
    category: str = Form(...),
    description: str = Form("")
):
    # Esqueleto: aquí se procesarían los archivos
    # Por ahora solo cierra el modal y muestra mensaje de éxito
    return HTMLResponse(
        '<div class="p-4 text-green-700">Documentos subidos correctamente.</div>',
        status_code=202
    )

@router.get("/documents/list", response_class=HTMLResponse)
async def document_list(request: Request):
    return templates.TemplateResponse("document_list.html", {"request": request})
