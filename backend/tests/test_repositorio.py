from datetime import datetime

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from app.infra.dados_iniciais import carregar_dados_iniciais
from app.infra.database import criar_engine, criar_tabelas
from app.infra.models import AlertaModel, DispositivoModel
from app.infra.repositorio import buscar_dispositivo, listar_alertas, listar_dispositivos


@pytest.fixture
def sessao():
    engine = criar_engine("sqlite://")  # banco em memória: some ao fim do teste
    criar_tabelas(engine)
    with sessionmaker(bind=engine)() as sessao:
        yield sessao
    engine.dispose()


def contar(sessao, modelo) -> int:
    return sessao.scalar(select(func.count()).select_from(modelo))


def test_dados_iniciais_gravam_quando_o_banco_esta_vazio(sessao):
    gravou = carregar_dados_iniciais(sessao)

    assert gravou is True
    assert contar(sessao, DispositivoModel) == 2
    assert contar(sessao, AlertaModel) == 1


def test_dados_iniciais_nao_duplicam_quando_ja_ha_dados(sessao):
    carregar_dados_iniciais(sessao)

    gravou_de_novo = carregar_dados_iniciais(sessao)

    assert gravou_de_novo is False
    assert contar(sessao, DispositivoModel) == 2
    assert contar(sessao, AlertaModel) == 1


def test_listar_dispositivos_devolve_todos(sessao):
    carregar_dados_iniciais(sessao)

    ids = {d.id for d in listar_dispositivos(sessao)}

    assert ids == {"AA:BB:CC:DD:EE:01", "AA:BB:CC:DD:EE:02"}


def test_listar_dispositivos_devolve_lista_vazia_sem_dados(sessao):
    assert listar_dispositivos(sessao) == []


def test_buscar_dispositivo_existente(sessao):
    carregar_dados_iniciais(sessao)

    dispositivo = buscar_dispositivo(sessao, "AA:BB:CC:DD:EE:02")

    assert dispositivo is not None
    assert dispositivo.nivel_risco == "risco"


def test_buscar_dispositivo_inexistente_devolve_none(sessao):
    carregar_dados_iniciais(sessao)

    assert buscar_dispositivo(sessao, "nao-existe") is None


def test_listar_alertas_do_mais_recente_para_o_mais_antigo(sessao):
    carregar_dados_iniciais(sessao)  # traz o "alerta-1", de 18/10/2026 14:01:30
    sessao.add(
        AlertaModel(
            id="alerta-2",
            dispositivo_id="AA:BB:CC:DD:EE:02",
            descricao="Alerta mais novo",
            nivel_risco="atencao",
            timestamp=datetime(2026, 11, 7, 9, 0, 0),
        )
    )
    sessao.commit()

    ids = [a.id for a in listar_alertas(sessao)]

    assert ids == ["alerta-2", "alerta-1"]
