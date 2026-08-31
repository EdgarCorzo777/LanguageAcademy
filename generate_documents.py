import sys
from pathlib import Path

# Ensure root and backend are in python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))
sys.path.insert(0, str(BASE_DIR / "backend" / "src"))

try:
    from backend.src.generate_documents import generate_business_documents
except ImportError:
    from src.generate_documents import generate_business_documents

if __name__ == "__main__":
    paths = generate_business_documents()
    print(f"Generated {len(paths)} business documents in data/ directory:")
    for path in paths:
        print(f" - {path}")
