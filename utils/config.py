import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Astra")
    CHAT_DB_PATH = os.getenv("CHAT_DB_PATH", "data/chat_history.db")
    APP_TIMEZONE = os.getenv("APP_TIMEZONE", "Asia/Kolkata")
