from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.infra.database import criar_engine, criar_tabelas
from app.infra.models import AlertaModel, DispositivoModel


@pytest.fixture
def sessao():
    engine = criar_engine("sqlite://")  # banco em memória: some ao fim do teste
    criar_tabelas(engine)
    with sessionmaker(bind=engine)() as sessao:
        yield sessao
    engine.dispose()


def novo_dispositivo(id: str = "AA:BB:CC:DD:EE:01") -> DispositivoModel:
    return DispositivoModel(
        id=id,
        nome="ESP32 - Sensor Temperatura",
        ip="192.168.4.11",
        ultima_atividade=datetime(2026, 11, 7, 14, 0, 0),
        nivel_risco="normal",
        score_risco=0.12,
    )


def test_salva_e_le_dispositivo(sessao):
    sessao.add(novo_dispositivo())
    sessao.commit()

    lido = sessao.get(DispositivoModel, "AA:BB:CC:DD:EE:01")

    assert lido is not None
    assert lido.nome == "ESP32 - Sensor Temperatura"
    assert lido.score_risco == 0.12
    assert lido.ultima_atividade == datetime(2026, 11, 7, 14, 0, 0)


def test_salva_alerta_ligado_a_um_dispositivo(sessao):
    sessao.add(novo_dispositivo())
    sessao.add(
        AlertaModel(
            id="alerta-1",
            dispositivo_id="AA:BB:CC:DD:EE:01",
            descricao="Porta Telnet (23) aberta detectada",
            nivel_risco="risco",
            timestamp=datetime(2026, 11, 7, 14, 1, 0),
        )
    )
    sessao.commit()

    alerta = sessao.get(AlertaModel, "alerta-1")

    assert alerta is not None
    assert alerta.dispositivo_id == "AA:BB:CC:DD:EE:01"


def test_alerta_de_dispositivo_inexistente_e_recusado(sessao):
    sessao.add(
        AlertaModel(
            id="alerta-orfao",
            dispositivo_id="nao-existe",
            descricao="Alerta sem dispositivo",
            nivel_risco="risco",
            timestamp=datetime(2026, 11, 7, 14, 1, 0),
        )
    )

    with pytest.raises(IntegrityError):
        sessao.commit()