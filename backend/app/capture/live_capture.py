import pyshark


def capturar_trafego(interface: str, bpf_filter: str = "", tshark_path: str | None = None):
    """Escuta uma interface de rede ao vivo e devolve os pacotes brutos, um a um.

    interface: nome ou número da interface (ex: 'Wi-Fi' ou '5' no Windows, 'wlan0' no Linux)
    bpf_filter: filtro opcional em sintaxe BPF, ex: 'tcp port 23'
    tshark_path: caminho do tshark, vindo de quem chama (None = procurar no PATH)

    Roda para sempre: quem consome decide quando parar e deve fechar o gerador.
    """
    captura = pyshark.LiveCapture(interface=interface, bpf_filter=bpf_filter, tshark_path=tshark_path)
    try:
        for pacote in captura.sniff_continuously():
            yield pacote
    finally:
        captura.close()
