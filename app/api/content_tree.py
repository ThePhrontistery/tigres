"""
FastAPI API routes for content tree.
"""
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
import re
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/content-tree")
def content_tree_page(request: Request):
    """Renderiza el árbol de contenidos desde plantilla.txt SOLO si existe el funcional generado."""
    funcional_path = Path("static/uploads/funcional_generado.md")
    tree = []
    if funcional_path.exists():
        plantilla_path = Path("plantilla.txt")
        if plantilla_path.exists():
            lines = [line.strip() for line in plantilla_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            current = None
            for line in lines:
                m = re.match(r"^(\d+)\.\s*(.+)", line)
                m2 = re.match(r"^(\d+)\.(\d+)\s*(.+)", line)
                if m and not m2:
                    # Título principal
                    current = {"title": m.group(2), "num": m.group(1), "children": []}
                    tree.append(current)
                elif m2 and current:
                    # Subtítulo
                    current["children"].append({"title": m2.group(3), "num": f"{m2.group(1)}.{m2.group(2)}"})
    # Si no existe el funcional, tree estará vacío y el índice no se mostrará
    return templates.TemplateResponse("content_tree/index.html", {"request": request, "tree": tree})
