# 03 — Backend e Contrato da API (API-First)

**Responsável sugerido:** Desenvolvedor Backend (API)

## 1. Por que API-First

A ideia é fechar o **contrato** (quais endpoints existem, o que cada um recebe e devolve) **antes** de o Frontend e o Backend começarem a implementar de verdade. Assim, o time de Frontend pode construir contra dados falsos (mocks) que seguem exatamente esse contrato, enquanto o Backend implementa a lógica real — sem um travar o outro.

## 2. Setup do ambiente

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install fastapi uvicorn[standard] pyshark pydantic pytest httpx
```

Estrutura mínima para começar:
```
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes.py
│   ├── domain/
│   ├── capture/
│   └── infra/
├── tests/
├── requirements.txt
└── Dockerfile
```

Rodando localmente:
```bash
uvicorn app.main:app --reload --port 8000
```
Acessem `http://localhost:8000/docs` — o FastAPI gera a documentação Swagger automaticamente a partir do código. **Esse Swagger gerado é a fonte de verdade do contrato**, mais confiável do que qualquer descrição escrita à mão.

## 3. Modelos de dados (Pydantic)

```python
# app/api/schemas.py
from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class NivelRisco(str, Enum):
    NORMAL = "normal"
    ATENCAO = "atencao"
    RISCO = "risco"

class Dispositivo(BaseModel):
    id: str                  # MAC address ou identificador único
    nome: str                # ex: "ESP32 - Sensor Temperatura"
    ip: str
    ultima_atividade: datetime
    nivel_risco: NivelRisco
    score_risco: float       # 0.0 a 1.0, calculado pelo PSO

class Alerta(BaseModel):
    id: str
    dispositivo_id: str
    descricao: str           # ex: "Porta Telnet (23) aberta detectada"
    nivel_risco: NivelRisco
    timestamp: datetime

class MitigacaoRequest(BaseModel):
    acao: str                 # ex: "bloquear_porta", "bloquear_ip"
    justificativa: str | None = None
```

## 4. Contrato de endpoints (v1)

| Método | Rota | Descrição | Corpo/Resposta |
|---|---|---|---|
| GET | `/health` | Healthcheck simples | `200 {"status": "ok"}` |
| GET | `/devices` | Lista todos os dispositivos conhecidos | `200 [Dispositivo]` |
| GET | `/devices/{device_id}` | Detalhe de um dispositivo | `200 Dispositivo` / `404` |
| GET | `/alerts` | Lista alertas, mais recentes primeiro | `200 [Alerta]` |
| POST | `/devices/{device_id}/mitigate` | Aciona uma ação de mitigação | body `MitigacaoRequest` → `200 {"status": "mitigado"}` |
| WS | `/ws/alerts` | Canal WebSocket para atualizações em tempo real | mensagens JSON no formato `Alerta` ou `Dispositivo` |

### Exemplo de rota (FastAPI)
```python
# app/api/routes.py
from fastapi import APIRouter, HTTPException
from app.api.schemas import Dispositivo, MitigacaoRequest

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/devices", response_model=list[Dispositivo])
def listar_dispositivos():
    ...  # buscar do repositório (infra/)

@router.get("/devices/{device_id}", response_model=Dispositivo)
def detalhe_dispositivo(device_id: str):
    dispositivo = ...  # buscar
    if dispositivo is None:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
    return dispositivo

@router.post("/devices/{device_id}/mitigate")
def mitigar(device_id: str, request: MitigacaoRequest):
    ...  # executar ação (ver docs/06-SEGURANCA.md)
    return {"status": "mitigado"}
```

### Exemplo de WebSocket
```python
# app/main.py (trecho)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.api.ws_manager import ConnectionManager

app = FastAPI(title="HomeGuard API")
manager = ConnectionManager()

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # mantém a conexão viva
    except WebSocketDisconnect:
        manager.active_connections.remove(websocket)
```

## 5. Erros — padrão de resposta

Todo erro deve seguir este formato (FastAPI já faz isso por padrão com `HTTPException`):
```json
{
  "detail": "Mensagem legível do erro"
}
```

| Código | Quando usar |
|---|---|
| `400` | Corpo da requisição inválido |
| `404` | Dispositivo/alerta não encontrado |
| `422` | Erro de validação do Pydantic (gerado automaticamente) |
| `500` | Erro inesperado — logar sempre, nunca expor detalhes internos ao cliente |

## 6. Testes

```python
# tests/test_devices.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_listar_dispositivos_vazio():
    response = client.get("/devices")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

Rodar: `pytest tests/ -v`

## 7. Checklist antes de abrir PR nesta camada

- [ ] Toda rota nova tem `response_model` definido.
- [ ] Toda rota nova tem pelo menos um teste em `tests/`.
- [ ] O Swagger (`/docs`) reflete exatamente o que está documentado aqui — se divergir, atualizem este arquivo.
