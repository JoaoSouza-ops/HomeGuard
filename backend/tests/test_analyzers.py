from types import SimpleNamespace as NS

import pytest

from app.domain.analyzers.factory import AnalyzerFactory


def test_tcp_telnet_e_insegura():
    pacote = NS(tcp=NS(dstport="23"), length="60")
    f = AnalyzerFactory.get_analyzer("tcp").extract_features(pacote)
    assert f == {"port": 23, "is_insecure_port": True, "payload_size": 60, "src_ip": None, "src_mac": None}


def test_tcp_porta_segura():
    pacote = NS(tcp=NS(dstport="443"), length="60")
    assert AnalyzerFactory.get_analyzer("TCP").extract_features(pacote)["is_insecure_port"] is False


def test_udp_mqtt():
    pacote = NS(udp=NS(dstport="1883"), length="60")
    assert AnalyzerFactory.get_analyzer("udp").extract_features(pacote)["is_mqtt"] is True


def test_protocolo_nao_suportado():
    with pytest.raises(ValueError):
        AnalyzerFactory.get_analyzer("ICMP")
