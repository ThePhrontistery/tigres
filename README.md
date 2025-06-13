# AI Web Template

Un proyecto base minimalista que combina **FastAPI** (backend Python), **Jinja2** (motor de plantillas HTML), y **HTMX** (interactividad web reactiva), todo gestionado con [uv](https://github.com/astral-sh/uv).
Incluye además soporte para **TailwindCSS** (estilos modernos) y carga automática de variables de entorno.

---

## Requisitos previos

* **Python 3.12 o superior**
  Recomendamos usar siempre una versión reciente de Python para asegurar compatibilidad.
* **uv**
  Es una herramienta moderna de gestión de entornos y dependencias para Python.
  Instálala una vez con:

  ```bash
  pipx install uv
  ```

  Más información: [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)

---

## Primeros pasos

```bash
# 1. Clona el repositorio y entra en la carpeta del proyecto
git clone <repo-url> ai-web-template
cd ai-web-template

# 2. Instala automáticamente todas las dependencias, crea el entorno virtual y el archivo de lock
uv sync

# 3a. Inicia el servidor de desarrollo (modo básico)
python -m app

# 3b. O bien, inicia el servidor con recarga automática (hot reload)
uv run -- uvicorn app.__main__:app --reload
```

* El comando `uv sync` lee el archivo **pyproject.toml**, instala todas las dependencias necesarias, crea un entorno virtual aislado, y guarda el estado en **uv.lock**.
* Si quieres desarrollo con recarga automática (ideal mientras editas el código), usa la opción 3b.

---

## Cómo añadir o actualizar dependencias

Cuando necesites nuevas librerías o quieras actualizar alguna existente, utiliza:

```bash
uv add nombre_paquete@latest    # Añade y bloquea la versión más reciente
uv sync                        # Sincroniza el entorno con el lockfile
```

Esto asegura que todo el equipo utilice exactamente las mismas versiones.

---

## Variables de entorno

Las variables de entorno (por ejemplo, puertos, modo desarrollo/producción, etc.) se gestionan en un archivo `.env`.

1. Copia el ejemplo y edítalo según tus necesidades:

   ```bash
   cp .env.example .env
   ```
2. Estas variables se cargarán automáticamente al arrancar la app, gracias a `python-dotenv` (ver `app/__init__.py`).

---

## Arquitectura y buenas prácticas

* El backend utiliza **FastAPI**, con rutas definidas en la carpeta `app/api/`.
* Las vistas HTML se gestionan con **Jinja2** en la carpeta `templates/`, extendiendo siempre `base.html`.
* La interactividad se basa en **HTMX** para peticiones asíncronas sin recargar la página.
* Los estilos están hechos con **TailwindCSS** (CDN).
* El proyecto está pensado para un desarrollo limpio, modular y fácil de mantener.

---

## Instrucciones personalizadas para GitHub Copilot

En el archivo `.github/copilot-instructions.md` encontrarás detalles sobre la arquitectura y recomendaciones de uso, para que GitHub Copilot genere código siguiendo las convenciones y tecnologías del proyecto.

