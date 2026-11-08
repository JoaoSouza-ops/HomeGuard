from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.infra.config import dados_iniciais_ligados
from app.api.routes_pso import router as router_pso
from app.infra.dados_iniciais import carregar_dados_iniciais
from app.infra.database import SessionLocal, criar_tabelas


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Roda uma vez quando o servidor sobe: garante as tabelas e, se a variável
    # CARREGAR_DADOS_INICIAIS estiver ligada, os dados de exemplo
    criar_tabelas()
    if dados_iniciais_ligados():
        with SessionLocal() as sessao:
            carregar_dados_iniciais(sessao)
    yield


app = FastAPI(title="API DO HOMEGUARD", lifespan=lifespan)
app.include_router(router)
app.include_router(router_pso)
