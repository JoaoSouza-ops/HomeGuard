from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.infra.dados_iniciais import carregar_dados_iniciais
from app.infra.database import SessionLocal, criar_tabelas


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Roda uma vez quando o servidor sobe: garante as tabelas e os dados iniciais
    criar_tabelas()
    with SessionLocal() as sessao:
        carregar_dados_iniciais(sessao)
    yield


app = FastAPI(title="API DO HOMEGUARD", lifespan=lifespan)
app.include_router(router)
