from abc import ABC, abstractmethod


def extrair_origem(packet) -> dict:
    """Devolve o IP e o MAC de origem do pacote.

    O IP vem da camada IPv4 (packet.ip) ou, se ela não existir, da IPv6
    (packet.ipv6). O MAC vem da camada Ethernet (packet.eth).
    Quando a camada ou o campo não existe, o valor é None.
    """
    camada_ip = getattr(packet, "ip", None)
    camada_ipv6 = getattr(packet, "ipv6", None)
    camada_eth = getattr(packet, "eth", None)

    src_ip = getattr(camada_ip, "src", None)
    if src_ip is None:
        src_ip = getattr(camada_ipv6, "src", None)

    return {
        "src_ip": src_ip,
        "src_mac": getattr(camada_eth, "src", None),
    }


class PacketAnalyzer(ABC):
    @abstractmethod
    def extract_features(self, packet) -> dict:
        """Recebe um pacote pyshark e devolve um dicionário de features de risco."""
        ...

