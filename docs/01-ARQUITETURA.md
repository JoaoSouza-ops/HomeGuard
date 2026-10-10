# 01 — Arquitetura do Sistema

## 1. Visão geral (Contexto)

```
┌──────────────┐        tráfego de rede        ┌──────────────────────┐
│  ESP32 "A"   │ ───────────────────────────▶  │                      │
│ (normal/MQTT)│                                │   Rede de Testes     │
└──────────────┘                                │   (isolada — ver     │
┌──────────────┐        tráfego de rede         │   docs/02)           │
│  ESP32 "B"   │ ───────────────────────────▶  │                      │
│ (vulnerável/ │                                └──────────┬───────────┘
│  Telnet)     │                                            │ captura (TShark/pyshark)
└──────────────┘                                            ▼
                                                   ┌───────────────────┐
                                                   │  Backend (FastAPI)│
                                                   │  - Ingestão       │
                                                   │  - Extração de    │
                                                   │    features       │
                                                   │  - Motor PSO      │
                                                   │  - API REST/WS    │
                                                   └─────────┬─────────┘
                                                             │ HTTP / WebSocket
                                                             ▼
                                                   ┌───────────────────┐
                                                   │ Frontend (React)  │
                                                   │ "Casa Virtual"    │
                                                   └───────────────────┘
```

## 2. Camadas do Backend (Arquitetura em Camadas / Hexagonal simplificada)

O backend é dividido em 4 camadas, cada uma com uma responsabilidade única. **Nenhuma camada deve pular a outra** (ex: a camada de API nunca lê pacotes de rede diretamente).

```
backend/
├── app/
│   ├── capture/        # Camada de Captura — só sabe "ouvir a rede" e devolver pacotes brutos
│   ├── domain/         # Camada de Domínio — regras de negócio: features, risco, dispositivos
│   │   ├── analyzers/  # Padrão Strategy (ver seção 3)
│   │   └── pso/        # Motor de otimização (ver docs/04)
│   ├── api/            # Camada de API — rotas FastAPI, validação de entrada/saída (schemas Pydantic)
│   └── infra/          # Camada de Infraestrutura — banco de dados, MQTT, configuração
├── tests/
└── main.py
```

**Por que separar assim:** se amanhã vocês trocarem `pyshark` por outra lib de captura, só a pasta `capture/` muda. Se trocarem SQLite por Postgres, só `infra/` muda. Isso facilita trabalho paralelo da equipe sem um módulo quebrar o outro.

## 3. Padrões de projeto aplicados (com justificativa)

### Strategy — análise de pacotes por protocolo
Problema: TCP, UDP e ICMP têm campos e riscos diferentes. Um `if/elif` gigante fica difícil de manter e testar.
Solução: cada protocolo implementa uma interface comum `PacketAnalyzer`.

```python
# app/domain/analyzers/base.py
from abc import ABC, abstractmethod

class PacketAnalyzer(ABC):
    @abstractmethod
    def extract_features(self, packet) -> dict:
        """Recebe um pacote pyshark e devolve um dicionário de features de risco."""
        ...

# app/domain/analyzers/tcp_analyzer.py
class TcpAnalyzer(PacketAnalyzer):
    def extract_features(self, packet) -> dict:
        return {
            "port": int(packet.tcp.dstport),
            "is_insecure_port": int(packet.tcp.dstport) in {23, 21, 80},  # Telnet, FTP, HTTP
            "payload_size": int(packet.length),
        }

# app/domain/analyzers/udp_analyzer.py
class UdpAnalyzer(PacketAnalyzer):
    def extract_features(self, packet) -> dict:
        return {
            "port": int(packet.udp.dstport),
            "is_mqtt": int(packet.udp.dstport) == 1883,
            "payload_size": int(packet.length),
        }
```

### Factory — escolha do analisador certo
```python
# app/domain/analyzers/factory.py
class AnalyzerFactory:
    _analyzers = {
        "TCP": TcpAnalyzer(),
        "UDP": UdpAnalyzer(),
    }

    @classmethod
    def get_analyzer(cls, protocol: str) -> PacketAnalyzer:
        analyzer = cls._analyzers.get(protocol.upper())
        if analyzer is None:
            raise ValueError(f"Protocolo não suportado: {protocol}")
        return analyzer
```

### Observer / Pub-Sub — propagação de alertas em tempo real
Quando o motor PSO reclassifica um dispositivo, o frontend precisa saber **sem dar refresh na página**. Usamos um WebSocket como canal de notificação: o backend publica o evento, e todo cliente conectado (Observer) recebe.

```python
# app/api/ws_manager.py
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)
```

## 4. Fluxo de dados (passo a passo)

1. ESP32 envia tráfego (MQTT ou Telnet) na rede de testes.
2. `capture/` captura o pacote via `pyshark` (modo live ou lendo `.pcap`).
3. `AnalyzerFactory` escolhe o `PacketAnalyzer` certo pelo protocolo.
4. As features extraídas alimentam o motor PSO (`domain/pso/`), que devolve um score de risco por dispositivo (0.0 a 1.0) e uma classificação (`Normal`, `Atenção`, `Risco`).
5. O resultado é salvo no banco (via `infra/`) e publicado via WebSocket (`ConnectionManager.broadcast`).
6. O frontend React atualiza o card do dispositivo em tempo real.
7. Se o usuário clicar em "Mitigar" no dashboard, o frontend chama `POST /devices/{id}/mitigate`, que aciona a ação de bloqueio (ver `docs/06-SEGURANCA.md`).

## 5. Decisões de arquitetura e trade-offs

| Decisão | Alternativa considerada | Por que escolhemos esta |
|---|---|---|
| FastAPI | Flask | Geração automática de documentação OpenAPI/Swagger, suporte nativo a `async` (importante para WebSocket) e validação de dados com Pydantic |
| React separado | Streamlit/Dash | Streamlit é mais rápido para prototipar, mas não separa bem frontend/backend nem permite trabalho 100% paralelo das duas frentes — decisão já confirmada pela equipe em `00-PREMISSAS.md` |
| WebSocket para alertas | Polling HTTP a cada N segundos | Menor latência e menor carga no backend; mais alinhado a como dashboards de segurança reais funcionam |
| Docker Compose | Kubernetes | Escopo do projeto não justifica a complexidade operacional do K8s |

## 6. O que documentar quando o código evoluir

Sempre que uma decisão de arquitetura mudar, adicionem uma linha na tabela da seção 5 — isso é o que a banca chama de "arquitetura documentada e justificada".
