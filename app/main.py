"""FastAPI app entrypoint, router registration, middleware, and startup logic."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.auth import router as auth_router
from app.api.main_views import router as main_views_router
from app.api.documents import router as documents_router
from app.api.markdown import router as markdown_router
from app.api.content_tree import router as content_tree_router
from app.api.markdown_editor import router as markdown_editor_router
from app.api.chat import router as chat_router
from app.api.vector import router as vector_router
from app.api.documents_download import router as documents_download_router
from app.db.session import init_db
import app.logging  # noqa: F401

app = FastAPI()

# Mount static files (if needed)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(auth_router)
app.include_router(main_views_router)
app.include_router(documents_router)
app.include_router(markdown_router)
app.include_router(content_tree_router)
app.include_router(markdown_editor_router)
app.include_router(chat_router)
app.include_router(vector_router)
app.include_router(documents_download_router)

@app.on_event("startup")
async def on_startup():
    await init_db()
