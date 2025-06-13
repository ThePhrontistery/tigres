"""Package root: loads .env and exposes the FastAPI instance."""
from dotenv import load_dotenv
load_dotenv()                       # .env -> os.environ early

from fastapi import FastAPI
app: FastAPI                        # populated in app.main
