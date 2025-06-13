"""Ping endpoint for health checks."""
from fastapi import APIRouter, Response

router = APIRouter()

@router.get("/ping", response_class=Response)
async def ping() -> Response:
    """Simple ping endpoint for health checks (HTML for HTMX).
    To return JSON instead, use:
    from fastapi.responses import JSONResponse
    @router.get("/ping", response_class=JSONResponse)
    async def ping() -> dict[str, str]:
        return {"message": "pong"}
    """
    return Response(content="<h1 class=\"text-green-600 text-2xl\">pong</h1>", media_type="text/html")
