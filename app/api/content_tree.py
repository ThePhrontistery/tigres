"""API para renderizar el árbol de contenido a partir de un markdown."""
from typing import List
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import re
from app.api.markdown import markdown_preview
from fastapi import Depends
import asyncio

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/content-tree", response_class=HTMLResponse)
async def content_tree(request: Request):
    # Leer el archivo template.md
    with open("template.md", encoding="utf-8") as f:
        md_text = f.read()
    tree  = parse_markdown_headings(md_text)
   
    return templates.TemplateResponse("content_tree.html", {"request": request, "tree": tree})

@router.get("/content-tree/section", response_class=HTMLResponse)
async def content_tree_section(request: Request, title: str = Query(...)):
    # Leer el archivo template.md
    with open("template.md", encoding="utf-8") as f:
        md_text = f.read()
    section_md = extract_section(md_text, title)
    
    return templates.TemplateResponse(
        "markdown_editor.html", {"request": request, "markdown": section_md or "", "preview": ""}
    )

def parse_markdown_headings(md_text: str, max_depth: int = 2) -> List[dict]:
    """Extrae los encabezados de nivel 1 y 2 de un markdown. """
    lines = md_text.splitlines()
    tree = []
    current = None
    for line in lines:
        if line.startswith("# "):
            current = {"title": line[2:].strip(), "children": []}
            tree.append(current)
        elif line.startswith("## ") and current and max_depth >= 2:
            current["children"].append({"title": line[3:].strip()})
    return tree

def extract_section(md_text: str, title: str) -> str:
    """Extrae el contenido de la sección indicada por el título y todo el contenido posterior."""
    lines = md_text.splitlines()
    capture = False
    section_lines = []
    for line in lines:
        if line.strip().startswith("#"):
            hashes, _, heading = line.partition(" ")
            if heading.strip() == title.strip():
                capture = True
        if capture:
            section_lines.append(line)
    return "\n".join(section_lines).strip()