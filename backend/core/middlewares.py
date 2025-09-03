from fastapi import Request
from fastapi.responses import JSONResponse

from backend.users.security import decode_access_token

protected_routes = [
    ("POST", "/api/v1/users/logout"),
    ("POST", "/api/v1/games"),
    ("GET", "/api/v1/games"),
    ("DELETE", "/api/v1/games"),
]


async def auth_middleware(request: Request, call_next):
    if (request.method, request.url.path) not in protected_routes:
        return await call_next(request)
    token = request.cookies.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
    user_id = decode_access_token(token).get("user_id")
    request.state.user_id = user_id
    return await call_next(request)
