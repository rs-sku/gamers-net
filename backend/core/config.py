from backend.core.settings import Settings


CORS_CONFIG = {
    "allow_origins": [f"http://{Settings.FRONTEND_HOST}:{Settings.FRONTEND_PORT}"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
