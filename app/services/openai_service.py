"""
Servicio para generación de análisis funcional usando Azure OpenAI.
"""
from typing import List
import os
import openai
from openai import AzureOpenAI
from docx import Document
from PyPDF2 import PdfReader
import asyncio
from pathlib import Path

def extract_text_from_file(file_path: str) -> str:
    """Extrae texto de un archivo PDF, DOCX o TXT."""
    if file_path.lower().endswith(".pdf"):
        try:
            reader = PdfReader(file_path)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            return f"[No se pudo extraer texto del PDF: {os.path.basename(file_path)}]"
    elif file_path.lower().endswith(".docx"):
        try:
            doc = Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            return f"[No se pudo extraer texto del DOCX: {os.path.basename(file_path)}]"
    else:
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return f"[No se pudo leer el archivo: {os.path.basename(file_path)}]"

def parse_plantilla_structure(plantilla_path: str) -> list:
    """Parses plantilla.txt y devuelve la estructura como lista de dicts."""
    import re
    tree = []
    if Path(plantilla_path).exists():
        lines = [line.strip() for line in Path(plantilla_path).read_text(encoding="utf-8").splitlines() if line.strip()]
        current = None
        for line in lines:
            m = re.match(r"^(\d+)\.\s*(.+)", line)
            m2 = re.match(r"^(\d+)\.(\d+)\s*(.+)", line)
            if m and not m2:
                current = {"title": m.group(2), "num": m.group(1), "children": []}
                tree.append(current)
            elif m2 and current:
                current["children"].append({"title": m2.group(3), "num": f"{m2.group(1)}.{m2.group(2)}"})
    return tree

def generate_funcional_analysis(file_paths: List[str]) -> str:
    """Genera un análisis funcional siguiendo exactamente la estructura de plantilla.txt y usando Azure OpenAI."""
    import re
    estructura = parse_plantilla_structure("plantilla.txt")
    docs_content = []
    for path in file_paths:
        if os.path.basename(path) == "funcional_generado.md":
            continue
        content = extract_text_from_file(path)
        docs_content.append(f"# {os.path.basename(path)}\n\n{content}")
    docs_text = "\n\n".join(docs_content)
    # Construir plantilla como texto plano para el prompt
    def plantilla_to_text(tree: list) -> str:
        txt = ""
        for node in tree:
            txt += f"{node['num']}. {node['title']}\n"
            for child in node.get("children", []):
                txt += f"{child['num']} {child['title']}\n"
        return txt.strip()
    plantilla_text = plantilla_to_text(estructura)
    # Construir el prompt
    prompt = (
        "Eres un analista funcional experto. Tu tarea es generar un documento funcional en formato Markdown, siguiendo ESTRICTAMENTE la estructura dada a continuación. "
        "Para cada sección y subsección, utiliza la información relevante de los documentos proporcionados. Si no hay información suficiente para una sección, deja un marcador '(Completar sección)'. "
        "No omitas ninguna sección ni subtítulo, aunque no haya contenido.\n\n"
        f"ESTRUCTURA DEL DOCUMENTO (usa exactamente estos títulos y subtítulos):\n{plantilla_text}\n\n"
        f"DOCUMENTOS DE REFERENCIA:\n{docs_text}\n\n"
        "Genera el documento funcional en Markdown, usando encabezados '#', '##', '###' según corresponda."
    )
    # Llamada a Azure OpenAI
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2023-05-15",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )
    try:
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "Eres un asistente de IA experto en análisis funcional."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=4096,
        )
        ai_md = response.choices[0].message.content
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return f"[ERROR] {str(e)}\nTRACEBACK:\n{tb}"
    # Validar que todas las secciones de la plantilla estén presentes
    def section_in_output(section_title: str, output: str) -> bool:
        # Busca el título como encabezado Markdown
        pattern = re.compile(rf"^#+\\s*{re.escape(section_title)}", re.MULTILINE)
        return bool(pattern.search(output))
    # Reconstruir el markdown si falta alguna sección
    def build_section_md(node, output):
        md = f"\n\n## {node['num']}. {node['title']}\n"
        if node.get("children"):
            for child in node["children"]:
                child_title = f"{child['num']} {child['title']}"
                if not section_in_output(child_title, output):
                    md += f"\n### {child['num']} {child['title']}\n(Completar sección)\n"
        else:
            if not section_in_output(f"{node['num']}. {node['title']}", output):
                md += "(Completar sección)\n"
        return md
    # Agregar secciones faltantes
    validated_md = ai_md
    for section in estructura:
        # Sección principal
        if not section_in_output(f"{section['num']}. {section['title']}", validated_md):
            validated_md += build_section_md(section, validated_md)
        # Subsecciones
        for child in section.get("children", []):
            child_title = f"{child['num']} {child['title']}"
            if not section_in_output(child_title, validated_md):
                validated_md += f"\n### {child['num']} {child['title']}\n(Completar sección)\n"
    # Eliminar cualquier índice textual del árbol de contenidos al final del documento funcional
    def remove_content_tree_index(md: str) -> str:
        import re
        # Busca un bloque que empiece por 'Índice' o 'Árbol de contenidos' y lo elimina
        pattern = re.compile(r"(^#+\s*(Índice|Índice de contenidos|Árbol de contenidos)[\s\S]+?)(?=^#|\Z)", re.MULTILINE | re.IGNORECASE)
        return re.sub(pattern, '', md).strip()
    validated_md = remove_content_tree_index(validated_md)
    # Eliminar cualquier índice textual que aparezca después del glosario
    def remove_index_after_glossary(md: str) -> str:
        import re
        # Busca el encabezado del glosario
        glossary_pattern = re.compile(r"^(#+\s*9\.\s*Glosario.*)$", re.MULTILINE | re.IGNORECASE)
        match = glossary_pattern.search(md)
        if not match:
            return md
        glossary_end = match.end()
        # Busca el primer encabezado de sección después del glosario
        next_header = re.search(r"^#+\s*\d+\.\s*", md[glossary_end:], re.MULTILINE)
        if next_header:
            # Hay otra sección después del glosario, no eliminar nada
            return md
        # Si no hay más secciones, elimina cualquier bloque de índice textual después del glosario
        # Busca patrones típicos de índice textual
        index_pattern = re.compile(r"(^#+\s*(Índice|Índice de contenidos|Árbol de contenidos)[\s\S]+$)", re.MULTILINE | re.IGNORECASE)
        before = md[:glosario_end]
        after = md[glosario_end:]
        after = re.sub(index_pattern, '', after).strip()
        return before + after
    validated_md = remove_index_after_glossary(validated_md)
    # Eliminar cualquier índice textual (Índice, Índice de contenidos, Árbol de contenidos) al final del documento
    def remove_trailing_index(md: str) -> str:
        import re
        # Busca un bloque de índice al final del documento (después del último encabezado real)
        pattern = re.compile(r"(^#+\s*(Índice|Índice de contenidos|Árbol de contenidos)[\s\S]*$)", re.MULTILINE | re.IGNORECASE)
        return re.sub(pattern, '', md).rstrip()
    validated_md = remove_trailing_index(validated_md)
    return validated_md.strip()

async def ask_azure_openai(message: str, document_content: str) -> str:
    """Consulta Azure OpenAI con o sin contexto de documento funcional."""
    if document_content.strip():
        prompt = (
            "Eres un asistente experto en análisis funcional. Responde la consulta del usuario usando únicamente la información relevante del siguiente documento funcional en Markdown.\n\n"
            f"DOCUMENTO FUNCIONAL:\n{document_content}\n\n"
            f"PREGUNTA DEL USUARIO: {message}"
        )
    else:
        prompt = (
            "Eres un asistente de IA. Responde la consulta del usuario de forma clara y útil.\n\n"
            f"PREGUNTA DEL USUARIO: {message}"
        )
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2023-05-15",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )
    response = await asyncio.to_thread(
        client.chat.completions.create,
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": "Eres un asistente de IA experto."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=1024,
    )
    return response.choices[0].message.content
