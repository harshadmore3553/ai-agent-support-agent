from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = Path(os.getenv("KNOWLEDGE_DIR", ROOT_DIR / "knowledge-base"))
ORDERS_FILE = Path(os.getenv("ORDERS_FILE", ROOT_DIR / "data" / "orders.json"))

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TOP_K = int(os.getenv("TOP_K", "6"))
MIN_RETRIEVAL_SCORE = float(os.getenv("MIN_RETRIEVAL_SCORE", "0.05"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
