import os
from pathlib import Path

from dotenv import load_dotenv

# backend/app/infra/config.py -> a raiz do repositório está 3 níveis acima da pasta infra
RAIZ_REPO = Path(__file__).resolve().parents[3]
load_dotenv(RAIZ_REPO / ".env")

# Usado quando DATABASE_URL não está definida. O caminho é relativo a quem
# roda o programa: rodando de dentro de backend/, o arquivo fica em backend/homeguard.db
DATABASE_URL_PADRAO = "sqlite:///./homeguard.db"


def obter_tshark_path() -> str | None:
    """Caminho do tshark.exe, vindo da variável TSHARK_PATH.
    Devolve None se não estiver definida (o pyshark procura no PATH)."""
    return os.getenv("TSHARK_PATH") or None


def obter_database_url() -> str:
    """URL de conexão com o banco, vinda da variável DATABASE_URL.
    Para migrar para PostgreSQL, basta trocar o valor desta variável."""
    return os.getenv("DATABASE_URL") or DATABASE_URL_PADRAO