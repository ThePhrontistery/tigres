"""
FastAPI API routes for document list and upload.
"""
from fastapi import APIRouter, UploadFile, File, Request, HTTPException, BackgroundTasks, Body, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import List
import concurrent.futures
import logging
import traceback
import tempfile
import markdown
import pdfkit

from app.services.openai_service import generate_funcional_analysis
from docx import Document as DocxDocument

router = APIRouter()
templates = Jinja2Templates(directory="templates")
UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

documents_cache: List[str] = []

# Configuración básica de logging a fichero
logging.basicConfig(
    filename="app_error.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s",
)

@router.get("/documents/list", response_class=JSONResponse)
async def get_documents_list() -> list[str]:
    """Return the list of uploaded documents, excluyendo el funcional generado."""
    files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file() and f.name != "funcional_generado.md"]
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

@router.post("/documents/generate-funcional", response_class=JSONResponse)
async def generate_funcional(background_tasks: BackgroundTasks):
    """Genera un análisis funcional a partir de los documentos subidos, lo devuelve en memoria y lo guarda en un archivo interno."""
    files = [str(f) for f in UPLOAD_DIR.iterdir() if f.is_file()]
    if not files:
        return {"error": "No hay documentos para analizar."}
    loop = None
    try:
        import asyncio
        loop = asyncio.get_running_loop()
    except RuntimeError:
        pass
    def sync_generate():
        try:
            from app.services.openai_service import generate_funcional_analysis
            return generate_funcional_analysis(files)
        except Exception as e:
            tb = traceback.format_exc()
            # Loguea el error y el traceback en un fichero
            logging.error(f"Error generando el análisis funcional: {e}\nTRACEBACK:\n{tb}")
            return f"[ERROR] {str(e)}\nTRACEBACK:\n{tb}"
    if loop:
        analysis = await loop.run_in_executor(None, sync_generate)
    else:
        analysis = sync_generate()
    if analysis.startswith("[ERROR]"):
        return JSONResponse(status_code=500, content={"error": analysis})
    internal_path = UPLOAD_DIR / "funcional_generado.md"
    internal_path.write_text(analysis, encoding="utf-8")
    return {"funcional": analysis}

@router.post("/documents/update-funcional", response_class=JSONResponse)
async def update_funcional(data: dict = Body(...)) -> dict:
    """Actualiza el documento funcional en memoria y en el archivo funcional_generado.md."""
    content = data.get("content", "")
    internal_path = UPLOAD_DIR / "funcional_generado.md"
    internal_path.write_text(content, encoding="utf-8")
    return {"ok": True}

@router.get("/documents/export-funcional")
async def export_funcional(format: str = Query("docx", enum=["docx", "pdf"])):
    """Exporta el documento funcional a Word o PDF."""
    internal_path = UPLOAD_DIR / "funcional_generado.md"
    if not internal_path.exists():
        return JSONResponse(status_code=404, content={"error": "No existe el documento funcional generado."})
    content = internal_path.read_text(encoding="utf-8")
    if format == "docx":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            doc = DocxDocument()
            for line in content.splitlines():
                doc.add_paragraph(line)
            doc.save(tmp.name)
            tmp.flush()
            return FileResponse(tmp.name, filename="funcional_generado.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    elif format == "pdf":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            html = markdown.markdown(content)
            pdfkit.from_string(html, tmp.name)
            tmp.flush()
            return FileResponse(tmp.name, filename="funcional_generado.pdf", media_type="application/pdf")
    return JSONResponse(status_code=400, content={"error": "Formato no soportado."})
