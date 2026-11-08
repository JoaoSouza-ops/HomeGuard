"""Teste manual do repositorio: carrega os dados iniciais e le pelo repositorio.

Uso (dentro de backend/, com a venv ativa):
    python scripts/testar_repositorio.py

Usa a DATABASE_URL do .env (ou sqlite:///./homeguard.db se nao existir).
Os dados iniciais so sao gravados se a tabela de dispositivos estiver VAZIA.
Se o banco ja tiver linhas (por exemplo, do testar_banco.py), apague o arquivo
backend/homeguard.db antes (ele e ignorado pelo Git) para ver a carga acontecer.
"""
import sys
from pathlib import Path

# Permite "from app..." mesmo rodando o arquivo direto de scripts/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.infra.config import obter_database_url  # noqa: E402
from app.infra.dados_iniciais import carregar_dados_iniciais  # noqa: E402
from app.infra.database import SessionLocal, criar_tabelas  # noqa: E402
from app.infra.repositorio import buscar_dispositivo, listar_alertas, listar_dispositivos  # noqa: E402


def main() -> int:
    print(f"DATABASE_URL: {obter_database_url()}")
    criar_tabelas()

    with SessionLocal() as sessao:
        gravou = carregar_dados_iniciais(sessao)
        print("Dados iniciais:", "gravados agora" if gravou else "nao gravados (o banco ja tinha dados)")

        dispositivos = listar_dispositivos(sessao)
        alertas = listar_alertas(sessao)
        vulneravel = buscar_dispositivo(sessao, "AA:BB:CC:DD:EE:02")
        inexistente = buscar_dispositivo(sessao, "nao-existe")

        print(f"\nDispositivos ({len(dispositivos)}):")
        for d in dispositivos:
            print(f"  {d.id} | {d.nome} | {d.nivel_risco} | {d.score_risco}")

        print(f"\nAlertas ({len(alertas)}), mais recentes primeiro:")
        for a in alertas:
            print(f"  {a.timestamp} | {a.dispositivo_id} | {a.descricao}")

        print(f"\nbuscar_dispositivo('AA:BB:CC:DD:EE:02'): {vulneravel.nome if vulneravel else None}")
        print(f"buscar_dispositivo('nao-existe'): {inexistente}")

    ok = len(dispositivos) > 0 and vulneravel is not None and inexistente is None
    print("\nRESULTADO:", "PASSOU" if ok else "FALHOU")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
