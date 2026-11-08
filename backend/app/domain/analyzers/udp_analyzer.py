from app.domain.analyzers.base import PacketAnalyzer, extrair_origem


class UdpAnalyzer(PacketAnalyzer):
    def extract_features(self, packet) -> dict:
        porta = int(packet.udp.dstport)
        return {
            "port": porta,
            "is_mqtt": porta == 1883,
            "payload_size": int(packet.length),
            **extrair_origem(packet),
        }
