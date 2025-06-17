"""Servicio para ingesta y almacenamiento en base de datos vectorial usando LangChain."""
from datetime import datetime
from typing import List, Optional
from app.config import settings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
import sqlite3
import numpy as np
import os

VECTOR_DB_PATH = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
TABLE_NAME = "document_vectors"

# --- Inicialización de la tabla vectorial ---
def init_vector_table():
    conn = sqlite3.connect(VECTOR_DB_PATH)
    c = conn.cursor()
    c.execute(f'''
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            embedding BLOB NOT NULL,
            text TEXT NOT NULL,
            fecha_carga TEXT,
            file_name TEXT,
            file_path TEXT,
            proyecto TEXT,
            categoria TEXT,
            descripcion TEXT
        )''')
    conn.commit()
    conn.close()

async def ingest_document(
    text: str,
    file_name: str,
    file_path: str,
    categoria: str,
    descripcion: str,
    proyecto: str = "demo_metasketch",
):
    init_vector_table()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.SPLITTER_CHUNK_SIZE,
        chunk_overlap=settings.SPLITTER_CHUNK_OVERLAP_DOC,
    )
    docs = splitter.create_documents([text])
    # Metadatos
    fecha_carga = datetime.utcnow().isoformat()
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        openai_api_version=settings.AZURE_OPENAI_API_VERSION,        
    )
    conn = sqlite3.connect(VECTOR_DB_PATH)
    c = conn.cursor()
    for doc in docs:
        # Metadatos
        doc.metadata = {
            "fecha_carga": fecha_carga,
            "file_name": file_name,
            "file_path": file_path,
            "proyecto": proyecto,
            "categoria": categoria,
            "descripcion": descripcion,
        }
        # Embedding
        emb = await embeddings.aembed_query(doc.page_content)
        emb_blob = np.array(emb, dtype=np.float32).tobytes()
        c.execute(
            f"""
            INSERT INTO {TABLE_NAME} (embedding, text, fecha_carga, file_name, file_path, proyecto, categoria, descripcion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (emb_blob, doc.page_content, fecha_carga, file_name, file_path, proyecto, categoria, descripcion)
        )
    conn.commit()
    conn.close()

# Consulta vectorial: devuelve los fragmentos más similares a un texto
async def query_similar_chunks(query: str, top_k: int = 5) -> list[dict]:
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        openai_api_version="2024-02-15-preview",
    )
    query_emb = await embeddings.aembed_query(query)
    query_emb = np.array(query_emb, dtype=np.float32)
    conn = sqlite3.connect(VECTOR_DB_PATH)
    c = conn.cursor()
    c.execute(f"SELECT id, embedding, text, fecha_carga, file_name, file_path, proyecto, categoria, descripcion FROM {TABLE_NAME}")
    results = []
    for row in c.fetchall():
        emb = np.frombuffer(row[1], dtype=np.float32)
        score = float(np.dot(query_emb, emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb) + 1e-8))
        results.append({
            "id": row[0],
            "score": score,
            "text": row[2],
            "fecha_carga": row[3],
            "file_name": row[4],
            "file_path": row[5],
            "proyecto": row[6],
            "categoria": row[7],
            "descripcion": row[8],
        })
    conn.close()
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

# Obtener lista de proyectos únicos
def get_proyects() -> list[str]:
    conn = sqlite3.connect(VECTOR_DB_PATH)
    c = conn.cursor()
    c.execute(f"SELECT DISTINCT proyecto FROM {TABLE_NAME}")
    projects = [row[0] for row in c.fetchall() if row[0]]
    conn.close()
    return projects

# Obtener lista de documentos de un proyecto
def get_proyect_documents(proyecto: str) -> list[str]:
    conn = sqlite3.connect(VECTOR_DB_PATH)
    c = conn.cursor()
    c.execute(f"SELECT DISTINCT file_name FROM {TABLE_NAME} WHERE proyecto = ?", (proyecto,))
    docs = [row[0] for row in c.fetchall() if row[0]]
    conn.close()
    return docs

# Obtener todos los embeddings y metadatos de un documento
def get_documento(file_name: str) -> list[dict]:
    conn = sqlite3.connect(VECTOR_DB_PATH)
    c = conn.cursor()
    c.execute(f"SELECT id, embedding, text, fecha_carga, file_name, file_path, proyecto, categoria, descripcion FROM {TABLE_NAME} WHERE file_name = ?", (file_name,))
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "embedding": row[1],
            "text": row[2],
            "fecha_carga": row[3],
            "file_name": row[4],
            "file_path": row[5],
            "proyecto": row[6],
            "categoria": row[7],
            "descripcion": row[8],
        }
        for row in rows
    ]
