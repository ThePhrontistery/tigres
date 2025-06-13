# GitHub Copilot — Repository Custom Instructions  

- **Stack** – FastAPI backend (async, typed), Jinja2 templates, HTMX for partial-page updates, and **Tailwind CSS** (via CDN) for *all* styling.  
- **Python 3.12+** only; follow Black + Ruff conventions. Use explicit type hints and docstrings.
- Dependencies live in **pyproject.toml**; manage them with `uv sync`. Never commit a requirements.txt.
- Load environment variables from `.env` with `python-dotenv` (see `app/__init__.py`).  
- Put new API routes in `app/api/<feature>.py`, register them via `include_router` in `app/main.py`, and keep paths under `/api/...`.
- HTML lives in **templates/**; always extend `templates/base.html`. Inject Tailwind utility classes—avoid inline `<style>` and external CSS frameworks.
- HTMX is globally imported in `base.html`; prefer progressive-enhancement patterns (`hx-get`, `hx-post`, `hx-swap`, etc.).
- Serve static assets with `StaticFiles` if needed; path `/static`.
- Use Jinja2 for templating; avoid inline JavaScript in templates. Use `<script>` tags for JS files.
- Use `app/utils/` for utility functions, `app/services/` for business logic, and `app/models/` for Pydantic models.
- Use `app/db/` for database interactions; prefer SQLAlchemy ORM with async support.
- Use `app/auth/` for authentication and authorization logic; prefer OAuth2 with JWT tokens.
- Use `app/tests/` for unit and integration tests; follow pytest conventions.
- Use `app/config.py` for configuration settings; load from environment variables.
- Use `app/logging.py` for logging configuration; set up structured logging with JSON format.
- Use `app/middleware/` for custom middleware; register in `app/main.py`.
- Return Pydantic models (or dicts) from API endpoints; use `response_model` for schema clarity.
- Keep commits and code self-explanatory; reference issues when relevant.
