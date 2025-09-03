import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    BACKEND_HOST = os.getenv("BACKEND_HOST")
    BACKEND_PORT = os.getenv("BACKEND_PORT")
    FRONTEND_HOST = os.getenv("FRONTEND_HOST")
    FRONTEND_PORT = os.getenv("FRONTEND_PORT")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
