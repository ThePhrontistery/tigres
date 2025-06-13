"""Entry‑point & composition root."""
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.api.router import router as api_router

templates = Jinja2Templates(directory="templates")
app = FastAPI(title="AI Web Template")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Home"}
    )

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":             # `python -m app.main`
    import uvicorn
    
    uvicorn.run(
        "app.__main__:app",  # Import the FastAPI app instance,
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
