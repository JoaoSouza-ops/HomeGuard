import pyshark


def ler_pcap(caminho_arquivo: str, tshark_path: str | None = None):
    """Lê um arquivo .pcap e devolve os pacotes brutos, um a um."""
    captura = pyshark.FileCapture(caminho_arquivo, tshark_path=tshark_path)
    try:
        for pacote in captura:
            yield pacote
    finally:
        captura.close()


        