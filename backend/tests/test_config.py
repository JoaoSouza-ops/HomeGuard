from app.infra.config import obter_tshark_path


def test_devolve_caminho_quando_variavel_definida(monkeypatch):
    monkeypatch.setenv("TSHARK_PATH", r"C:\falso\tshark.exe")
    assert obter_tshark_path() == r"C:\falso\tshark.exe"


def test_devolve_none_quando_variavel_ausente(monkeypatch):
    monkeypatch.delenv("TSHARK_PATH", raising=False)
    assert obter_tshark_path() is None


def test_devolve_none_quando_variavel_vazia(monkeypatch):
    monkeypatch.setenv("TSHARK_PATH", "")
    assert obter_tshark_path() is None
