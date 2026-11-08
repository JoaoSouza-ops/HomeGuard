from fastapi.testclient import TestClient

from app.main import app

# O banco em memória com os dados iniciais é ligado automaticamente
# pelo conftest.py, então estes testes não tocam no homeguard.db.
client = TestClient(app)


def test_health():
    resposta = client.get("/health")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_listar_dispositivos_devolve_os_dados_iniciais():
    resposta = client.get("/devices")

    assert resposta.status_code == 200
    ids = {d["id"] for d in resposta.json()}
    assert ids == {"AA:BB:CC:DD:EE:01", "AA:BB:CC:DD:EE:02"}


def test_detalhe_do_dispositivo_vulneravel():
    resposta = client.get("/devices/AA:BB:CC:DD:EE:02")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["nivel_risco"] == "risco"
    assert corpo["score_risco"] == 0.87


def test_detalhe_de_dispositivo_inexistente_devolve_404():
    resposta = client.get("/devices/inexistente")

    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Dispositivo não encontrado"}


def test_listar_alertas():
    resposta = client.get("/alerts")

    assert resposta.status_code == 200
    alertas = resposta.json()
    assert len(alertas) == 1
    assert alertas[0]["dispositivo_id"] == "AA:BB:CC:DD:EE:02"


def test_mitigar_dispositivo_existente():
    resposta = client.post("/devices/AA:BB:CC:DD:EE:02/mitigate", json={"acao": "bloquear_porta"})

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "mitigado"}


def test_mitigar_dispositivo_inexistente_devolve_404():
    resposta = client.post("/devices/inexistente/mitigate", json={"acao": "bloquear_porta"})

    assert resposta.status_code == 404


def test_mitigar_sem_o_campo_acao_devolve_422():
    resposta = client.post("/devices/AA:BB:CC:DD:EE:02/mitigate", json={})

    assert resposta.status_code == 422
