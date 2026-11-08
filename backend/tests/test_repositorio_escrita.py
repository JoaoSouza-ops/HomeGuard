from datetime import datetime

import pytest
from sqlalchemy.orm import sessionmaker

from app.infra.database import criar_engine, criar_tabelas
from app.infra.repositorio import (
    buscar_dispositivo,
    listar_alertas,
    listar_dispositivos,
    registrar_alerta,
    salvar_dispositivo,
)


@pytest.fixture
def sessao():
    engine = criar_engine("sqlite://")  # banco em memória, começa vazio
    criar_tabelas(engine)
    with sessionmaker(bind=engine)() as sessao:
        yield sessao
    engine.dispose()


def salvar_exemplo(sessao, **mudancas):
    dados = {
        "device_id": "AA:BB:CC:DD:EE:10",
        "nome": "ESP32 - Teste",
        "ip": "192.168.4.50",
        "ultima_atividade": datetime(2026, 11, 8, 10, 0, 0),
        "nivel_risco": "normal",
        "score_risco": 0.1,
    }
    dados.update(mudancas)
    return salvar_dispositivo(sessao, **dados)


def test_salvar_dispositivo_novo(sessao):
    salvar_exemplo(sessao)

    lido = buscar_dispositivo(sessao, "AA:BB:CC:DD:EE:10")

    assert lido is not None
    assert lido.nome == "ESP32 - Teste"
    assert lido.score_risco == 0.1


def test_salvar_dispositivo_existente_atualiza_sem_duplicar(sessao):
    salvar_exemplo(sessao)

    salvar_exemplo(sessao, nivel_risco="risco", score_risco=0.9)

    assert len(listar_dispositivos(sessao)) == 1
    lido = buscar_dispositivo(sessao, "AA:BB:CC:DD:EE:10")
    assert lido.nivel_risco == "risco"
    assert lido.score_risco == 0.9


def test_salvar_dispositivo_recusa_score_fora_da_faixa(sessao):
    with pytest.raises(ValueError, match="score_risco"):
        salvar_exemplo(sessao, score_risco=1.5)

    assert listar_dispositivos(sessao) == []


def test_salvar_dispositivo_recusa_nivel_invalido(sessao):
    with pytest.raises(ValueError, match="nivel_risco"):
        salvar_exemplo(sessao, nivel_risco="perigo")

    assert listar_dispositivos(sessao) == []


def test_registrar_alerta_aparece_na_listagem(sessao):
    salvar_exemplo(sessao)

    alerta = registrar_alerta(
        sessao,
        dispositivo_id="AA:BB:CC:DD:EE:10",
        descricao="Porta Telnet (23) aberta detectada",
        nivel_risco="risco",
        timestamp=datetime(2026, 11, 8, 10, 5, 0),
    )

    assert alerta.id
    assert [a.id for a in listar_alertas(sessao)] == [alerta.id]


def test_registrar_alerta_gera_ids_diferentes(sessao):
    salvar_exemplo(sessao)

    primeiro = registrar_alerta(sessao, dispositivo_id="AA:BB:CC:DD:EE:10", descricao="a", nivel_risco="atencao")
    segundo = registrar_alerta(sessao, dispositivo_id="AA:BB:CC:DD:EE:10", descricao="b", nivel_risco="atencao")

    assert primeiro.id != segundo.id


def test_registrar_alerta_de_dispositivo_inexistente_levanta_erro(sessao):
    with pytest.raises(ValueError, match="Dispositivo não encontrado"):
        registrar_alerta(sessao, dispositivo_id="nao-existe", descricao="x", nivel_risco="risco")

    assert listar_alertas(sessao) == []
