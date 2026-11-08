from types import SimpleNamespace

import pytest

from app.domain.analyzers.factory import AnalyzerFactory

ORIGEM_IPV4 = {
    "eth": SimpleNamespace(src="aa:bb:cc:dd:ee:01"),
    "ip": SimpleNamespace(src="192.168.4.11"),
}
ORIGEM_IPV6 = {
    "eth": SimpleNamespace(src="aa:bb:cc:dd:ee:01"),
    "ipv6": SimpleNamespace(src="fe80::1"),
}


def pacote_tcp(porta: str = "23", tamanho: str = "60", **camadas):
    return SimpleNamespace(tcp=SimpleNamespace(dstport=porta), length=tamanho, **camadas)


def pacote_udp(porta: str = "1883", tamanho: str = "80", **camadas):
    return SimpleNamespace(udp=SimpleNamespace(dstport=porta), length=tamanho, **camadas)


def test_tcp_porta_23_e_insegura():
    features = AnalyzerFactory.get_analyzer("TCP").extract_features(pacote_tcp("23", **ORIGEM_IPV4))
    assert features == {
        "port": 23,
        "is_insecure_port": True,
        "payload_size": 60,
        "src_ip": "192.168.4.11",
        "src_mac": "aa:bb:cc:dd:ee:01",
    }


def test_tcp_porta_443_nao_e_insegura():
    features = AnalyzerFactory.get_analyzer("TCP").extract_features(pacote_tcp("443", **ORIGEM_IPV4))
    assert features["is_insecure_port"] is False


def test_udp_porta_1883_e_mqtt():
    features = AnalyzerFactory.get_analyzer("UDP").extract_features(pacote_udp("1883", **ORIGEM_IPV4))
    assert features == {
        "port": 1883,
        "is_mqtt": True,
        "payload_size": 80,
        "src_ip": "192.168.4.11",
        "src_mac": "aa:bb:cc:dd:ee:01",
    }


def test_udp_outra_porta_nao_e_mqtt():
    features = AnalyzerFactory.get_analyzer("UDP").extract_features(pacote_udp("5353", **ORIGEM_IPV4))
    assert features["is_mqtt"] is False


def test_origem_ipv6_quando_nao_ha_ipv4():
    features = AnalyzerFactory.get_analyzer("TCP").extract_features(pacote_tcp("443", **ORIGEM_IPV6))
    assert features["src_ip"] == "fe80::1"
    assert features["src_mac"] == "aa:bb:cc:dd:ee:01"


def test_origem_none_quando_faltam_camadas():
    tcp = AnalyzerFactory.get_analyzer("TCP").extract_features(pacote_tcp("23"))
    udp = AnalyzerFactory.get_analyzer("UDP").extract_features(pacote_udp("1883"))
    assert tcp["src_ip"] is None and tcp["src_mac"] is None
    assert udp["src_ip"] is None and udp["src_mac"] is None


def test_factory_ignora_maiusculas_e_minusculas():
    assert AnalyzerFactory.get_analyzer("tcp") is AnalyzerFactory.get_analyzer("TCP")


def test_factory_recusa_protocolo_desconhecido():
    with pytest.raises(ValueError, match="Protocolo não suportado: ICMP"):
        AnalyzerFactory.get_analyzer("ICMP")
