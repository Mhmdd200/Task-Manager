import logging
import time
import uuid

from fastapi import Request

logger = logging.getLogger(__name__)


async def log_requests(request: Request, call_next):
    request_id = uuid.uuid4().hex
    start = time.perf_counter()
    # request.state is how middleware hands data to endpoints
    request.state.request_id = request_id

    try:
        response = await call_next(request)
    except Exception:
        # a crash makes call_next raise, so there is no response to add headers to.
        # uvicorn prints the traceback after the re-raise, so logger.error is enough here
        duration = (time.perf_counter() - start) * 1000
        logger.error(
            "%s %s status=500 duration=%.2fms request_id=%s",
            request.method, request.url.path, duration, request_id,
        )
        raise

    duration = (time.perf_counter() - start) * 1000

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{duration:.2f}"

    # only the path: never log headers, bodies or query strings (they can hold secrets)
    logger.info(
        "%s %s status=%s duration=%.2fms request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration,
        request_id,
    )

    return response
