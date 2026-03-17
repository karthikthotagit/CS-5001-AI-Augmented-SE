import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST  = os.getenv("OLLAMA_HOST",  "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:0.6b")

ANALYZER_PORT = int(os.getenv("ANALYZER_PORT", "8101"))
REVIEWER_PORT = int(os.getenv("REVIEWER_PORT", "8102"))
