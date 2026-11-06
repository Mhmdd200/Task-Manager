from fastapi import Request
from fastapi.responses import JSONResponse


def handle_crash(request: Request, exc: Exception):
    request_id = request.state.request_id
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "request_id": request_id},
        headers={"X-Request-ID": request_id},
    )
