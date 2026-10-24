from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="API DO HOMEGUARD")
app.include_router(router)