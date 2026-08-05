import os
from pathlib import Path
from dotenv import load_dotenv

# Define base directory of the backend
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(dotenv_path=BASE_DIR / ".env")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI", "http://localhost:5173/auth/callback"
)

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://localhost/consumer_attention"
)
SECRET_KEY = os.getenv("SECRET_KEY", "consumer_attention_secret_key")
