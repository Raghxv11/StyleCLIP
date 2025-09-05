import os
from dotenv import load_dotenv

# Ensure we load the .env located in the backend/ directory explicitly
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
_DOTENV_PATH = os.path.join(_BASE_DIR, ".env")
load_dotenv(_DOTENV_PATH)

class Settings:
    # MongoDB configuration
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017") 
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "clothing_db")

    API_KEY: str = os.getenv("API_KEY", "your-api-key-here")

    # AWS configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")

    # Application settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "mysecretkey")
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"  
    PORT: int = int(os.getenv("PORT", 8000))  # Default port to 8000

settings = Settings()
