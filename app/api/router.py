"""Example endpoints — extend or split into sub‑routers as needed."""
from fastapi import APIRouter

from .ping import router as ping_router
from .documents import router as documents_router
from .auth import router as auth_router

router = APIRouter()
router.include_router(ping_router)
router.include_router(documents_router)
router.include_router(auth_router)

