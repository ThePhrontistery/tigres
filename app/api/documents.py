"""API y vistas parciales para gestión de documentos."""
from fastapi import APIRouter, Request, UploadFile, File, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import status
import os
from app.services.vector_store import (
    ingest_document,
    get_proyect_documents,
    get_documento,
    delete_documento,
)
import aiofiles
from pathlib import Path
from datetime import datetime

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
    return templates.TemplateResponse(
        "documents_upload.html", {"request": request, "categories": categories}
    )


@router.get("/documents/close-modal", response_class=HTMLResponse)
async def close_modal(request: Request):
    # Devuelve un div vacío para cerrar el modal
    return HTMLResponse("")


@router.post(
    "/api/documents/upload",
    response_class=HTMLResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_documents(
    request: Request,
    files: list[UploadFile] = File(...),
    category: str = Form(...),
    description: str = Form(""),
):
    upload_dir = Path("uploaded_docs")
    upload_dir.mkdir(exist_ok=True)
    for file in files:
        file_path = upload_dir / file.filename
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)
        # Extraer texto (asumimos txt para demo, para otros tipos usar extractor adecuado)
        text = content.decode("utf-8", errors="ignore")
        await ingest_document(
            text=text,
            file_name=file.filename,
            file_path=str(file_path),
            categoria=category,
            descripcion=description,
            proyecto="demo_metasketch",
        )
    return templates.TemplateResponse(
        "modal_success.html",
        {"request": request, "message": "Documentos subidos correctamente."}
    )


@router.get("/documents/list", response_class=HTMLResponse)
async def document_list(request: Request, deleted_message: str = None):
    """Lista de documentos, con mensaje opcional tras borrado."""
    documents = get_proyect_documents("demo_metasketch")
    return templates.TemplateResponse(
        "document_list.html", {"request": request, "documents": documents, "deleted_message": deleted_message}
    )


@router.get("/documents/view", response_class=HTMLResponse)
async def view_document(request: Request, file_name: str):
    """Renderiza los detalles y vista previa de un documento."""
    doc_list = get_documento(file_name)
    document = doc_list[0] if doc_list else None
    return templates.TemplateResponse(
        "document_detail.html",
        {"request": request, "document": document},
    )


@router.delete("/api/documents/delete", response_class=HTMLResponse)
async def api_delete_document(request: Request, file_name: str = Query(...)):
    """Elimina un documento y muestra modal de éxito, luego recarga la lista."""
    ok = await delete_documento(file_name)
    message = "Documento eliminado" if ok else "No se pudo eliminar el documento"
    return templates.TemplateResponse(
        "modal_success.html", {"request": request, "message": message}
    )
