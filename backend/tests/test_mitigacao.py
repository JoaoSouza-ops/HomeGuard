import pytest
from app.domain.mitigacao import executar_mitigacao

def test_executar_mitigacao_bloquear_porta_valido():
    # Não deve levantar exceção
    executar_mitigacao("bloquear_porta", "192.168.4.15")

def test_executar_mitigacao_bloquear_ip_valido():
    executar_mitigacao("bloquear_ip", "192.168.4.15")

def test_executar_mitigacao_acao_invalida():
    with pytest.raises(ValueError, match="Ação não suportada"):
        executar_mitigacao("acao_desconhecida", "192.168.4.15")

def test_executar_mitigacao_ip_invalido():
    with pytest.raises(ValueError, match="IP inválido"):
        executar_mitigacao("bloquear_porta", "999.999.999.999")

