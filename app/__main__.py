"""Entrypoint para ejecutar la app con `python -m app`."""
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
