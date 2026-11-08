import pytest
from sqlalchemy.orm import sessionmaker

from app.api.dependencias import get_sessao
from app.infra.dados_iniciais import carregar_dados_iniciais
from app.infra.database import criar_engine, criar_tabelas
from app.main import app


@pytest.fixture(autouse=True)
def banco_em_memoria():
    """Em todo teste, as rotas usam um banco em memória com os dados iniciais.

    Assim os testes nunca encostam no arquivo homeguard.db de desenvolvimento
    e cada teste começa com o mesmo estado.
    """
    engine = criar_engine("sqlite://")
    criar_tabelas(engine)
    fabrica = sessionmaker(bind=engine)
    with fabrica() as sessao:
        carregar_dados_iniciais(sessao)

    def sessao_de_teste():
        with fabrica() as sessao:
            yield sessao

    app.dependency_overrides[get_sessao] = sessao_de_teste
    yield
    app.dependency_overrides.clear()
    engine.dispose()
