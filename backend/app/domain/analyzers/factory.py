from app.domain.analyzers.base import PacketAnalyzer
from app.domain.analyzers.tcp_analyzer import TcpAnalyzer
from app.domain.analyzers.udp_analyzer import UdpAnalyzer


class AnalyzerFactory:
    _analyzers = {
        "TCP": TcpAnalyzer(),
        "UDP": UdpAnalyzer(),
    }

    @classmethod
    def get_analyzer(cls, protocol: str) -> PacketAnalyzer:
        analyzer = cls._analyzers.get(protocol.upper())
        if analyzer is None:
            raise ValueError(f"Protocolo não suportado: {protocol}")
        return analyzer