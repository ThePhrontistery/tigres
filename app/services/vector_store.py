"""Servicio para ingesta y almacenamiento en base de datos vectorial usando LangChain."""
from datetime import datetime
from typing import List, Optional
from app.config import settings
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader,PyPDFLoader, UnstructuredWordDocumentLoader, UnstructuredPowerPointLoader, UnstructuredExcelLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
import sqlite3
import numpy as np
import os
from langchain_community.vectorstores import SQLiteVSS

VECTOR_DB_PATH = settings.VECTOR_DATABASE_URL.replace("sqlite+aiosqlite:///", "")
VECTOR_DATABASE_TABLE = settings.VECTOR_DATABASE_TABLE
TABLE_NAME = "document_vectors"


async def ingest_document(
    text: str,
    file_name: str,
    file_path: str,
    categoria: str,
    descripcion: str,
    proyecto: str = "demo_metasketch",
):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.SPLITTER_CHUNK_SIZE,
        chunk_overlap=settings.SPLITTER_CHUNK_OVERLAP_DOC,
    )

    if file_name.endswith(".pdf"):
        loader=PyPDFLoader(file_path)
    elif file_name.endswith(".docx"):
        loader=UnstructuredWordDocumentLoader(file_path, encoding="utf-8")
    elif file_name.endswith(".pptx"):
        loader=UnstructuredPowerPointLoader(file_path, encoding="utf-8")
    elif file_name.endswith(".xlsx"):
        loader=UnstructuredExcelLoader(file_path, encoding="utf-8")
    elif file_name.endswith(".md"):
        loader=UnstructuredMarkdownLoader(file_path, encoding="utf-8")
    else:
        loader=TextLoader(file_path)

    docs=loader.load()

    for doc in docs:
        # Metadatos
        doc.metadata = {
            "fecha_carga": datetime.utcnow().isoformat(),
            "file_name": file_name,
            "file_path": file_path,
            "proyecto": proyecto,
            "categoria": categoria,
            "descripcion": descripcion,
        }
    
    print(f"Docs cargados: {len(docs)}")    
    final_documents=splitter.split_documents(docs)
    
    # Metadatos
    
    #embeddings = AzureOpenAIEmbeddings(
    #    azure_deployment=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    #    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    #    api_key=settings.AZURE_OPENAI_API_KEY,
    #    openai_api_version=settings.AZURE_OPENAI_API_VERSION,        
    #)
    
    embeddings = AzureOpenAIEmbeddings(model=settings.AZURE_OPENAI_EMBEDDING_MODEL)
    
    db = Chroma(
        persist_directory=VECTOR_DB_PATH,
        collection_name=VECTOR_DATABASE_TABLE,
        embedding_function=embeddings,
    )

    db.add_documents(final_documents)



# Obtener lista de proyectos únicos
def get_proyects() -> list[str]:
    """
    Obtiene la lista ordenada y única de proyectos almacenados en el vector store.

    Returns:
        list[str]: Lista de nombres de proyectos.
    """
    embeddings = AzureOpenAIEmbeddings(model=settings.AZURE_OPENAI_EMBEDDING_MODEL)
    db = Chroma(
        persist_directory=VECTOR_DB_PATH,
        collection_name=VECTOR_DATABASE_TABLE,
        embedding_function=embeddings,
    )
    # Obtener solo los metadatos de todos los documentos
    results = db.get(include=["metadatas"])
    proyectos: set[str] = set()
    for meta in results.get("metadatas", []):
        if meta and "proyecto" in meta and meta["proyecto"]:
            proyectos.add(meta["proyecto"])
    return sorted(proyectos)


def get_proyect_documents(proyecto: str) -> list[dict]:
    """
    Retrieve all unique documents for a given project from the vector store.

    Args:
        proyecto: Project identifier.

    Returns:
        List of dicts with file name and metadata (no duplicate file_names).
    """
    embeddings = AzureOpenAIEmbeddings(model=settings.AZURE_OPENAI_EMBEDDING_MODEL)
    db = Chroma(
        persist_directory=VECTOR_DB_PATH,
        collection_name=VECTOR_DATABASE_TABLE,
        embedding_function=embeddings,
    )

    results = db.get(where={"proyecto": proyecto})
    seen_files: set[str] = set()
    project_docs: list[dict] = []
    for meta in results.get("metadatas", []):
        file_name = meta.get("file_name")
        if file_name and file_name not in seen_files:
            seen_files.add(file_name)
            project_docs.append({
                "file_name": file_name,
                "metadata": meta,
            })

    return project_docs

from typing import Any

def get_documento(file_name: str) -> list[dict[str, Any]]:
    """
    Devuelve los documentos asociados a un archivo específico usando filtro en el vector store.
    """
    embeddings = AzureOpenAIEmbeddings(model=settings.AZURE_OPENAI_EMBEDDING_MODEL)
    db = Chroma(
        persist_directory=VECTOR_DB_PATH,
        collection_name=VECTOR_DATABASE_TABLE,
        embedding_function=embeddings,
    )
    # Usar filtro para traer solo los documentos con ese file_name
    docs = db.similarity_search(
        query="",  # o algún texto relevante si buscas por similitud
        k=1000,    # ajusta según lo esperado
        filter={"file_name": file_name}
    )
    return [
        {
            "text": doc.page_content,
            **doc.metadata,
        }
        for doc in docs
        if doc.metadata  # opcional: asegura que metadata existe
    ]

async def query_similar_chunks(query: str, top_k: int = 5) -> list[dict]:
    embeddings = AzureOpenAIEmbeddings(model=settings.AZURE_OPENAI_EMBEDDING_MODEL)
    db = Chroma(
        persist_directory=VECTOR_DB_PATH,
        collection_name=VECTOR_DATABASE_TABLE,
        embedding_function=embeddings,
    )
    docs = db.similarity_search(query, k=top_k)
    results = []
    for doc in docs:
        meta = doc.metadata if hasattr(doc, 'metadata') else {}
        results.append({
            "text": doc.page_content,
            **meta,
        })
    return results

async def delete_documento(file_name: str) -> bool:
    """
    Elimina todos los documentos asociados a un archivo específico del vector store.

    Args:
        file_name: Nombre del archivo cuyos documentos se eliminarán.

    Returns:
        bool: True si se eliminaron documentos, False si no se encontró ninguno.
    """
    embeddings = AzureOpenAIEmbeddings(model=settings.AZURE_OPENAI_EMBEDDING_MODEL)
    db = Chroma(
        persist_directory=VECTOR_DB_PATH,
        collection_name=VECTOR_DATABASE_TABLE,
        embedding_function=embeddings,
    )

    # Buscar documentos con ese file_name usando filtro
    docs = db.get(where={"file_name": file_name})
    if not docs.get("ids"):
        return False

    # Eliminar por filtro (más eficiente y seguro)
    db.delete(where={"file_name": file_name})
    return True
