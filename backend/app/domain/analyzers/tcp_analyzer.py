from app.domain.analyzers.base import PacketAnalyzer

PORTAS_INSEGURAS = {23, 21, 80}  # Telnet, FTP, HTTP


class TcpAnalyzer(PacketAnalyzer):
    def extract_features(self, packet) -> dict:
        porta = int(packet.tcp.dstport)
        return {
            "port": porta,
            "is_insecure_port": porta in PORTAS_INSEGURAS,
            "payload_size": int(packet.length),
        }