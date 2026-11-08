import os
from pathlib import Path
from dotenv import load_dotenv
# backend/app/infra/config.py -> a raiz do repositório está 3 níveis acima da pasta infra
RAIZ_REPO = Path(__file__).resolve().parents[3]
load_dotenv(RAIZ_REPO / ".env")

def obter_tshark_path() -> str | None:
    """Caminho do tshark.exe, vindo da variável TSHARK_PATH.
    Devolve None se não estiver definida (o pyshark então procura no PATH)."""
    return os.getenv("TSHARK_PATH") or None
