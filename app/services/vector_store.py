"""Servicio para ingesta y almacenamiento en base de datos vectorial usando LangChain."""
from datetime import datetime
from typing import List, Optional
from app.config import settings
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader,PyPDFLoader
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
    embeddings = AzureOpenAIEmbeddings(model=settings.AZURE_OPENAI_EMBEDDING_MODEL)
    db = Chroma(
        persist_directory=VECTOR_DB_PATH,
        collection_name=VECTOR_DATABASE_TABLE,
        embedding_function=embeddings,
    )
    # Recuperar todos los metadatos de los documentos
    metadatas = [doc.metadata for doc in db.similarity_search("", k=10000)]
    proyectos = set()
    for meta in metadatas:
        if meta and "proyecto" in meta and meta["proyecto"]:
            proyectos.add(meta["proyecto"])
    return sorted(proyectos)


# Obtener lista de documentos de un proyecto
def get_proyect_documents(proyecto: str) -> list[dict]:
    embeddings = AzureOpenAIEmbeddings(model=settings.AZURE_OPENAI_EMBEDDING_MODEL)
    db = Chroma(
        persist_directory=VECTOR_DB_PATH,
        collection_name=VECTOR_DATABASE_TABLE,
        embedding_function=embeddings,
    )
   
    project_docs: list[dict] = []
    for doc in db.similarity_search("", k=10000):
        meta = doc.metadata
        if meta and "proyecto" in meta and meta["proyecto"]:
            project_doc = {            
                "file_name": meta["file_name"],            
                "metadata": meta,
            }
            project_docs.append(project_doc)
    
    return project_docs

# Obtener el documento con su contenido y metadatos
def get_documento(file_name: str) -> list[dict]:
    embeddings = AzureOpenAIEmbeddings(model=settings.AZURE_OPENAI_EMBEDDING_MODEL)
    db = Chroma(
        persist_directory=VECTOR_DB_PATH,
        collection_name=VECTOR_DATABASE_TABLE,
        embedding_function=embeddings,
    )
    docs = db.similarity_search("", k=10000)
    result = []
    for doc in docs:
        meta = doc.metadata if hasattr(doc, 'metadata') else {}
        if meta and meta.get("file_name") == file_name:
            result.append({
                "text": doc.page_content,
                **meta,
            })
    return result

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
    embeddings = AzureOpenAIEmbeddings(model=settings.AZURE_OPENAI_EMBEDDING_MODEL)
    db = Chroma(
        persist_directory=VECTOR_DB_PATH,
        collection_name=VECTOR_DATABASE_TABLE,
        embedding_function=embeddings,
    )
    docs = db.similarity_search("", k=10000)
    files_to_delete = []
    for doc in docs:
        meta = doc.metadata if hasattr(doc, 'metadata') else {}
        if meta and meta.get("file_name") == file_name :
            files_to_delete.append(meta["file_name"])

    if not files_to_delete:
        return False
    
    # Eliminar directamente de la tabla SQL
    # Eliminar documentos de la base vectorial por file_name en metadatos
    result = db._collection.delete(where={"file_name": {"$in": files_to_delete}})
    print(f"Resultado de la eliminación: {result}")
    
    return True
