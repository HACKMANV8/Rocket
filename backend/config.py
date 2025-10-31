import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('FLASK_ENV') == 'development'
    
    # MySQL Configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'mining_user')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'mining_password_456')
    MYSQL_DB = os.getenv('MYSQL_DATABASE', 'mining_data')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
    
    # ✅ UPDATED: ChromaDB Local Storage (not server)
    CHROMA_PERSIST_DIR = os.getenv('CHROMA_PERSIST_DIR', './chroma_data')
    
    # ✅ ADDED: Ollama Configuration (Free Local LLM)
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost')
    OLLAMA_PORT = os.getenv('OLLAMA_PORT', '11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')
    
    # API Keys
    MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY', '')
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')
    
    # Model Settings
    EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # RAG Settings
    TOP_K_RESULTS = 5
    MAX_RESPONSE_LENGTH = 500  # 3-4 sentences
    
    # Supported Languages for TTS
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'es': 'Spanish', 
        'fr': 'French',
        'de': 'German',
        'hi': 'Hindi',
        'zh': 'Chinese',
        'ar': 'Arabic',
        'pt': 'Portuguese'
    }
    
    # ✅ ADDED: Cache Settings
    TRANSFORMERS_CACHE = os.getenv('TRANSFORMERS_CACHE', './models_cache')
    HUGGINGFACE_HUB_CACHE = os.getenv('HUGGINGFACE_HUB_CACHE', './models_cache')