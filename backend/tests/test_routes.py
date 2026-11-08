import pytest
from fastapi.testclient import TestClient

# Só roda depois que a PR das rotas (app/api/routes.py) entrar na main.
pytest.importorskip("app.api.routes")

from app.main import app  # noqa: E402

client = TestClient(app)
ID_VULNERAVEL = "AA:BB:CC:DD:EE:02"


def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json() == {"status": "ok"}


def test_listar_e_detalhe():
    assert client.get("/devices").status_code == 200
    assert client.get(f"/devices/{ID_VULNERAVEL}").status_code == 200
    assert client.get("/devices/inexistente").status_code == 404


def test_mitigar():
    r = client.post(f"/devices/{ID_VULNERAVEL}/mitigate", json={"acao": "bloquear_porta"})
    assert r.status_code == 200
    assert client.post("/devices/nope/mitigate", json={"acao": "x"}).status_code == 404
    assert client.post(f"/devices/{ID_VULNERAVEL}/mitigate", json={}).status_code == 422
