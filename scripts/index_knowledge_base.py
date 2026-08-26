from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import KNOWLEDGE_DIR
from app.retrieval import Retriever

retriever = Retriever(KNOWLEDGE_DIR)
print(f"Indexed {len(retriever.chunks)} chunks from {KNOWLEDGE_DIR}")
