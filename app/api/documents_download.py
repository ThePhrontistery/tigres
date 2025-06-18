"""Endpoint para descargar documentos originales subidos."""
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()

@router.get("/api/documents/download")
def download_document(file_name: str = Query(...)):
    """Permite descargar el archivo original subido por nombre."""
    file_path = Path("uploaded_docs") / file_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(
        path=str(file_path),
        filename=file_name,
        media_type="application/octet-stream"
    )
