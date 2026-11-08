from pathlib import Path

from fastapi import APIRouter, Depends

from app.api.schemas import FeaturesJanela, RelatorioPSO, SimulacaoResultado, TreinoRequest
from app.domain.pso import servico
from app.domain.pso.modelo import FEATURES

router = APIRouter(prefix="/pso", tags=["pso"])


def get_caminho_pesos() -> Path:
    """Onde ficam os pesos. Nos testes é trocado por um arquivo temporário."""
    return servico.ARQUIVO_PESOS


@router.get("/pesos", response_model=RelatorioPSO)
def obter_pesos(caminho: Path = Depends(get_caminho_pesos)):
    """Pesos atuais + curva de convergência + métricas. Sem treino salvo,
    devolve os pesos padrão (iguais) sem métricas."""
    relatorio = servico.carregar_relatorio(caminho)
    if relatorio is None:
        return RelatorioPSO(features=list(FEATURES), pesos=servico.PESOS_PADRAO)
    return relatorio


@router.post("/treinar", response_model=RelatorioPSO)
def treinar(req: TreinoRequest | None = None, caminho: Path = Depends(get_caminho_pesos)):
    """Re-treina o PSO com o dataset de exemplo e salva os novos pesos."""
    req = req or TreinoRequest()
    return servico.treinar_e_salvar(
        caminho, semente=req.semente, n_particulas=req.particulas, iteracoes=req.iteracoes
    )


@router.post("/simular", response_model=SimulacaoResultado)
def simular(features: FeaturesJanela, caminho: Path = Depends(get_caminho_pesos)):
    """Calcula o score de uma janela hipotética com os pesos atuais."""
    return servico.pontuar(features.model_dump(), caminho)
