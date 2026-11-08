# HomeGuard

Sistema open source de monitoramento e classificação de risco para redes domésticas com dispositivos IoT. Captura tráfego de rede, classifica o risco de cada dispositivo usando **PSO (Particle Swarm Optimization)** e exibe tudo em um dashboard web interativo com suporte a resposta a incidentes (mitigação).

> **Projeto acadêmico — NEXUS (Engenharia da Computação) — ExpoTech 2026.2.**

---

## 🏗️ Arquitetura e Componentes

O sistema é dividido em camadas independentes e integradas:

```
┌─────────────────┐       tráfego de rede       ┌────────────────────────┐
│ ESP32 "A" (MQTT)│ ──────────────────────────▶ │  Rede / Broker         │
│ ESP32 "B" (Telnet)│                            │  (Mosquitto / Testes)  │
└─────────────────┘                             └───────────┬────────────┘
                                                            │ captura (TShark / pyshark)
                                                            ▼
┌───────────────────┐        REST / WebSocket       ┌────────────────────────┐
│  Frontend (React) │ ◀──────────────────────────── │  Backend (FastAPI)     │
│  - Casa Virtual   │                               │  - SQLite (SQLAlchemy) │
│  - Painel PSO     │ ────────────────────────────▶ │  - Motor PSO (NumPy)   │
│  - Mitigações     │     POST /devices/mitigate    │  - Mitigação Simulada  │
└───────────────────┘                               └────────────────────────┘
```

1. **Firmware (`firmware/`):**
   * **ESP "A" (Normal):** Publica temperatura simulada a cada 5 s via MQTT (`homeguard/sensores/temperatura`) na porta `1883`, com jitter, backoff exponencial e temporização não-bloqueante.
   * **ESP "B" (Vulnerável):** Abre porta TCP `23` (Telnet sem criptografia - CWE-319 / T1040) e expõe credenciais de teste (`admin:admin123`).
   * Testes unitários nativos com Unity (`firmware/test/test_core/`).

2. **Backend (`backend/`):**
   * **FastAPI + SQLAlchemy + SQLite:** endpoints REST para dispositivos, alertas e mitigação.
   * **WebSocket (`/ws/alerts`):** streaming de alertas em tempo real.
   * **Motor PSO (`backend/app/domain/pso/`):** otimizador implementado do zero com NumPy para calibrar pesos de 5 features de rede e calcular scores de risco normalizados (`0.0` a `1.0`).
   * **Mitigação (`backend/app/domain/mitigacao.py`):** validação de IP/porta e bloqueio simulado auditável.

3. **Frontend (`frontend/`):**
   * Single Page Application em React + Vite.
   * Planta interativa da **Casa Virtual**, cartões de dispositivos com medidores de risco, feed de alertas e **PsoPanel** com curva de convergência SVG e simulador de features.

4. **Infraestrutura (`infra/`):**
   * Orquestração com Docker Compose (`mosquitto`, `esp-sim`, `backend`, `web`, `caddy`).
   * Proxy reverso unificado com Caddy (HTTPS/HTTP).

---

## 🚀 Como Executar Localmente

### Opção 1: Via Docker Desktop (Recomendada)

Com o **Docker Desktop** aberto e em execução no Windows:

```powershell
# Sobe toda a pilha (Mosquitto + Simulador ESPs + Backend + Frontend + Caddy):
.\hg.cmd sim

# Verifica a saúde de todos os serviços (API, MQTT e Telnet):
.\hg.cmd check

# Acompanhar logs em tempo real:
.\hg.cmd logs backend
.\hg.cmd logs esp-sim

# Encerrar e parar os contêineres:
.\hg.cmd down

# Se precisar reiniciar do zero limpando o banco:
.\hg.cmd reset
```

* **Dashboard Web:** [http://localhost:8080](http://localhost:8080)
* **API Swagger / OpenAPI:** [http://localhost:8080/api/docs](http://localhost:8080/api/docs)
* **Simulador ESPs Telnet:** `localhost:2323`

---

### Opção 2: Nativamente no Windows (Sem Docker)

Se preferir executar cada serviço diretamente no host:

#### 1. Pré-requisitos
* Python 3.11+ instalado
* Node.js 20+ e npm instalados

#### 2. Backend
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Habilita dados iniciais simulados para demonstração:
$env:CARREGAR_DADOS_INICIAIS="true"

# Inicia o servidor:
uvicorn app.main:app --reload --port 8000
```
> API disponível em [http://localhost:8000](http://localhost:8000) (Docs em [http://localhost:8000/docs](http://localhost:8000/docs)).

#### 3. Frontend
Em outro terminal:
```powershell
cd frontend
npm install
npm run dev
```
> Dashboard disponível em [http://localhost:5173](http://localhost:5173).

#### 4. Simulador de ESPs (Opcional, sem hardware físico)
Em um terceiro terminal:
```powershell
# Simula a porta Telnet do dispositivo vulnerável:
$env:TELNET_PORT="2323"
python infra/simulator/sim_esp.py
```

---

## 🧪 Bateria de Testes Automatizados

### Testes do Backend (Python / pytest)
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest tests/ -v
```
Cobre analisadores de protocolo TCP/UDP, pipelines, banco SQLite, motor PSO e mitigação.

### Testes do Firmware (PlatformIO / Unity)
```powershell
cd firmware
pio test -e native
```

---

## 🔄 Como Resetar as Mitigações para Apresentação

Para reiniciar o status de demonstração e reabilitar o botão **"Mitigar"**:
1. No navegador ([http://localhost:8080](http://localhost:8080)), pressione **`F12`** para abrir o DevTools.
2. Na aba **Console**, execute:
   ```javascript
   localStorage.clear(); location.reload();
   ```

---

## 🎤 Roteiro de Apresentação (Pitch de 3 a 5 minutos)

### 1. O Problema (30s)
> *"Dispositivos IoT residenciais como lâmpadas, câmeras e sensores frequentemente utilizam firmwares inseguros, sem criptografia e com portas de gerenciamento abertas (como Telnet na porta 23). O usuário comum não sabe o que trafega na rede até que um dispositivo seja invadido."*

### 2. A Solução HomeGuard (45s)
> *"O HomeGuard atua como uma sentinela passiva na rede. Ele inspeciona o tráfego dos dispositivos IoT, extrai características de rede em tempo real, submete ao algoritmo de Inteligência Computacional PSO e apresenta visualmente o nível de risco em uma Casa Virtual, permitindo mitigar a ameaça com um clique."*

### 3. Como o Backend Funciona e se Integra ao PSO (1m 15s)
> *"O backend em FastAPI extrai cinco features comportamentais de cada dispositivo: taxa de pacotes suspeitos, uso de portas inseguras, desvio de volume, identificação de MAC desconhecido e frequência de conexões.*
> 
> *Em vez de definir pesos arbitrários por regras rígidas, utilizamos o algoritmo **PSO (Particle Swarm Optimization)**. O enxame explora o espaço pentadimensional de pesos para minimizar o erro quadrático médio em relação a um dataset rotulado. O modelo final opera de forma instantânea em produção, calculando o score ponderado e classificando o dispositivo em Normal, Atenção ou Risco."*

### 4. Integração com o Frontend e Mitigação ao Vivo (1m)
> *(Demonstrando o dashboard)*:
> *"No frontend em React, a Casa Virtual consome a API e WebSockets. Vemos aqui o ESP32 normal seguro e o ESP32 vulnerável em vermelho com score 0.87. Na aba de análise, exibimos a curva de aprendizado do PSO e o simulador interativo.*
> 
> *Ao clicar em **Mitigar**, o frontend aciona o endpoint `/devices/{id}/mitigate`. O backend valida as diretrizes de rede e registra o bloqueio imediato do tráfego do dispositivo vulnerável, neutralizando o vetor de ataque."*

---

## 📁 Estrutura do Repositório

```
HomeGuard/
├── backend/            # API FastAPI, repositório SQLite, analisadores e PSO
│   ├── app/
│   │   ├── api/        # Rotas REST, rotas /pso e WebSocket
│   │   ├── domain/     # Lógica do PSO, pipeline de features e mitigação
│   │   └── infra/      # Modelos SQLAlchemy, banco SQLite e configurações
│   └── tests/          # Suíte completa de testes com pytest
├── frontend/           # Dashboard React (Vite)
│   └── src/
│       ├── components/ # Casa Virtual, DeviceCard, PsoPanel e Mitigações
│       └── services/   # Integração com API REST e mocks
├── firmware/           # Código C/C++ dos ESP32 (esp_normal e esp_vulneravel)
├── infra/              # Docker Compose, Caddyfile e simulador dos ESPs
├── docs/               # Especificações completas (00 a 08)
└── hg.cmd / hg.sh      # CLI de automação local
```
