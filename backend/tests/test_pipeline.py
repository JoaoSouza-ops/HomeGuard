from types import SimpleNamespace

from app.domain.pipeline import PipelineFeatures

ORIGEM_IPV4 = {
    "eth": SimpleNamespace(src="aa:bb:cc:dd:ee:01"),
    "ip": SimpleNamespace(src="192.168.4.11"),
}


def pacote_tcp(porta: str = "23", tamanho: str = "60", **camadas):
    return SimpleNamespace(
        transport_layer="TCP", tcp=SimpleNamespace(dstport=porta), length=tamanho, **camadas
    )


def pacote_udp(porta: str = "1883", tamanho: str = "80", **camadas):
    return SimpleNamespace(
        transport_layer="UDP", udp=SimpleNamespace(dstport=porta), length=tamanho, **camadas
    )


def pacote_sem_transporte():
    return SimpleNamespace(transport_layer=None, length="42")


def pacote_protocolo_nao_suportado():
    return SimpleNamespace(transport_layer="SCTP", length="100")


def test_extrai_features_de_tcp_e_udp_com_origem():
    pipeline = PipelineFeatures()

    resultado = list(pipeline.processar([pacote_tcp(**ORIGEM_IPV4), pacote_udp(**ORIGEM_IPV4)]))

    assert resultado == [
        {
            "port": 23,
            "is_insecure_port": True,
            "payload_size": 60,
            "src_ip": "192.168.4.11",
            "src_mac": "aa:bb:cc:dd:ee:01",
        },
        {
            "port": 1883,
            "is_mqtt": True,
            "payload_size": 80,
            "src_ip": "192.168.4.11",
            "src_mac": "aa:bb:cc:dd:ee:01",
        },
    ]
    assert pipeline.processados == 2
    assert sum(pipeline.descartados.values()) == 0


def test_features_trazem_none_quando_origem_ausente():
    pipeline = PipelineFeatures()

    resultado = list(pipeline.processar([pacote_tcp()]))

    assert resultado[0]["src_ip"] is None
    assert resultado[0]["src_mac"] is None
    assert pipeline.processados == 1


def test_descarta_e_conta_pacote_sem_camada_de_transporte():
    pipeline = PipelineFeatures()

    resultado = list(pipeline.processar([pacote_sem_transporte(), pacote_tcp(**ORIGEM_IPV4)]))

    assert len(resultado) == 1
    assert pipeline.processados == 1
    assert pipeline.descartados["sem_camada_de_transporte"] == 1


def test_descarta_e_conta_protocolo_nao_suportado():
    pipeline = PipelineFeatures()

    resultado = list(pipeline.processar([pacote_protocolo_nao_suportado()]))

    assert resultado == []
    assert pipeline.descartados["nao_suportado_SCTP"] == 1


def test_contadores_acumulam_entre_chamadas():
    pipeline = PipelineFeatures()

    list(pipeline.processar([pacote_tcp(**ORIGEM_IPV4), pacote_sem_transporte()]))
    list(pipeline.processar([pacote_udp(**ORIGEM_IPV4), pacote_sem_transporte()]))

    assert pipeline.processados == 2
    assert pipeline.descartados["sem_camada_de_transporte"] == 2

