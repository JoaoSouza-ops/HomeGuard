from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from app.infra.config import obter_database_url

URLS_EM_MEMORIA = ("sqlite://", "sqlite:///:memory:")


class Base(DeclarativeBase):
    """Classe base de todos os modelos de tabela (ver models.py)."""


def criar_engine(url: str) -> Engine:
    """Cria o engine para a URL informada.

    Os ajustes específicos do SQLite ficam todos aqui, para que a troca por
    PostgreSQL mexa só neste arquivo (e na variável DATABASE_URL).
    """
    if not url.startswith("sqlite"):
        return create_engine(url)

    opcoes = {"connect_args": {"check_same_thread": False}}
    if url in URLS_EM_MEMORIA:
        # Banco em memória: todas as operações precisam usar a mesma conexão,
        # senão cada uma enxerga um banco vazio diferente.
        opcoes["poolclass"] = StaticPool

    engine = create_engine(url, **opcoes)

    @event.listens_for(engine, "connect")
    def _ativar_chaves_estrangeiras(conexao, _registro):
        # O SQLite ignora FOREIGN KEY por padrão e o PostgreSQL não.
        # Ligar aqui faz os dois se comportarem igual.
        cursor = conexao.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


engine = criar_engine(obter_database_url())
SessionLocal = sessionmaker(bind=engine)


def criar_tabelas(alvo: Engine | None = None) -> None:
    """Cria as tabelas que ainda não existem (não altera as que já existem)."""
    from app.infra import models  # noqa: F401  (registra os modelos em Base)

    Base.metadata.create_all(bind=alvo or engine)
