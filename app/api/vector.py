"""APIs para consulta sobre la tabla document_vectors."""
from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse
from app.services.vector_store import (
    get_proyects,
    get_proyect_documents,
    get_documento,
    query_similar_chunks,
    delete_documento,
)

router = APIRouter(prefix="/api/vector", tags=["vector"])

@router.get("/projects", response_class=JSONResponse)
def api_get_projects():
    return get_proyects()

@router.get("/project-documents", response_class=JSONResponse)
def api_get_project_documents(proyecto: str = Query(...)):
    return get_proyect_documents(proyecto)

@router.get("/document", response_class=JSONResponse)
def api_get_document(file_name: str = Query(...)):
    return get_documento(file_name)

@router.get("/similar", response_class=JSONResponse)
async def api_query_similar(query: str = Query(...), top_k: int = 5):
    results = await query_similar_chunks(query, top_k)
    return results

@router.delete("/document", response_class=JSONResponse, status_code=status.HTTP_200_OK)
async def api_delete_document(file_name: str = Query(...)):
    ok = await delete_documento(file_name)
    return {"success": ok}
