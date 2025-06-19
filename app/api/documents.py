"""
FastAPI API routes for document list and upload.
"""
from fastapi import APIRouter, UploadFile, File, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import List

router = APIRouter()
templates = Jinja2Templates(directory="templates")
UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

documents_cache: List[str] = []

@router.get("/documents/list", response_class=JSONResponse)
async def get_documents_list() -> list[str]:
    """Return the list of uploaded documents."""
    files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
    return files

@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Handle file uploads."""
    saved = []
    for file in files:
        dest = UPLOAD_DIR / file.filename
        with dest.open("wb") as f:
            f.write(await file.read())
        saved.append(file.filename)
    return {"uploaded": saved}

@router.get("/documents")
def documents_page(request: Request):
    """Render the document list page."""
    return templates.TemplateResponse("documents/list.html", {"request": request})

@router.delete("/documents/{filename}", response_class=JSONResponse)
def delete_document(filename: str):
    """Delete a document by filename."""
    file_path = UPLOAD_DIR / filename
    if file_path.exists() and file_path.is_file():
        file_path.unlink()
        return {"deleted": filename}
    raise HTTPException(status_code=404, detail="Documento no encontrado")
