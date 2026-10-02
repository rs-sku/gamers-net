from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, HTTPException):
        raise exc
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# TODO others

class NotFoundException(HTTPException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(status_code=404, detail=message)

    def __str__(self) -> str:
        return self.message
