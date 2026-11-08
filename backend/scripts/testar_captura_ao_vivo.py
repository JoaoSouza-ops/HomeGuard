"""Teste manual da captura AO VIVO: interface de rede -> capture -> pipeline -> features.

Uso (dentro de backend/, com a venv ativa):
    python scripts/testar_captura_ao_vivo.py 5
    python scripts/testar_captura_ao_vivo.py Wi-Fi --limite 100
    python scripts/testar_captura_ao_vivo.py 5 --filtro "tcp port 23"

O primeiro argumento e a interface (no Windows, o numero do "tshark -D", ex: 5).
Gere trafego enquanto roda (abra um site). Se der erro de permissao, abra o
PowerShell como Administrador. O caminho do TShark vem de TSHARK_PATH no .env.

Atencao: a saida mostra IPs e MACs reais da rede capturada.
"""
import argparse
import sys
from itertools import islice
from pathlib import Path

# Permite "from app..." mesmo rodando o arquivo direto de scripts/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.capture.live_capture import capturar_trafego  # noqa: E402
from app.domain.pipeline import PipelineFeatures  # noqa: E402
from app.infra.config import obter_tshark_path  # noqa: E402

EXEMPLOS = 5


def main() -> int:
    parser = argparse.ArgumentParser(description="Testa a captura ao vivo + pipeline")
    parser.add_argument("interface", help="interface de rede (numero do tshark -D, ou nome)")
    parser.add_argument("-n", "--limite", type=int, default=50, help="quantos pacotes capturar (padrao: 50)")
    parser.add_argument("-f", "--filtro", default="", help="filtro BPF opcional, ex: 'tcp port 23'")
    args = parser.parse_args()

    print(f"Interface: {args.interface} | filtro: {args.filtro or '(nenhum)'}")
    print(f"Capturando {args.limite} pacotes... gere trafego agora (abra um site).\n")

    pacotes = capturar_trafego(args.interface, args.filtro, obter_tshark_path())
    pipeline = PipelineFeatures()
    mostrados = 0

    try:
        for features in pipeline.processar(islice(pacotes, args.limite)):
            if mostrados < EXEMPLOS:
                mostrados += 1
                print(features)
    finally:
        pacotes.close()

    print("\nResumo:")
    print(f"  processados: {pipeline.processados}")
    print(f"  descartados: {dict(pipeline.descartados)}")

    ok = pipeline.processados > 0
    print("\nRESULTADO:", "PASSOU" if ok else "FALHOU (nenhum pacote TCP/UDP capturado)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
