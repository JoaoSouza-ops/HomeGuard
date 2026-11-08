from collections.abc import Iterator

from sqlalchemy.orm import Session

from app.infra.database import SessionLocal


def get_sessao() -> Iterator[Session]:
    """Abre uma sessão do banco para a requisição e fecha ao terminar.

    As rotas pedem a sessão com Depends(get_sessao). Nos testes, esta função
    é trocada por uma que usa um banco em memória (ver tests/conftest.py).
    """
    with SessionLocal() as sessao:
        yield sessao
