import os

from dotenv import load_dotenv

load_dotenv()


def get_required_setting(setting_name: str) -> str:
    setting = os.getenv(setting_name)
    if setting is None:
        raise ValueError("Required setting is not provided")
    return setting


class Settings:
    POSTGRES_HOST = get_required_setting("POSTGRES_HOST")
    POSTGRES_PORT = get_required_setting("POSTGRES_PORT")
    POSTGRES_DB = get_required_setting("POSTGRES_DB")
    POSTGRES_USER = get_required_setting("POSTGRES_USER")
    POSTGRES_PASSWORD = get_required_setting("POSTGRES_PASSWORD")
    BACKEND_HOST = get_required_setting("BACKEND_HOST")
    BACKEND_PORT = get_required_setting("BACKEND_PORT")
    FRONTEND_HOST = get_required_setting("FRONTEND_HOST")
    FRONTEND_PORT = get_required_setting("FRONTEND_PORT")
    SECRET_KEY = get_required_setting("SECRET_KEY")
    ALGORITHM = get_required_setting("ALGORITHM")
