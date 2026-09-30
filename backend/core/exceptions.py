from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, HTTPException):
        raise exc
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


class NotFoundException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
