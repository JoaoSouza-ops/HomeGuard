# 🛡️ HomeGuard — Monitoramento e Classificação Inteligente de Risco IoT

O **HomeGuard** é um sistema *open source* que funciona como um **"vigia inteligente" para redes Wi-Fi domésticas**. Ele monitora o tráfego de aparelhos de Internet das Coisas (IoT — como sensores, lâmpadas e câmeras inteligentes), calcula automaticamente uma **nota de risco de `0.0` a `1.0`** para cada aparelho usando Inteligência Computacional (**PSO — Particle Swarm Optimization**) e exibe tudo em tempo real em um painel visual (**Casa Virtual**), permitindo bloquear aparelhos vulneráveis com um clique.

> **Projeto Acadêmico Integrado — Equipe NEXUS (Engenharia da Computação — FECAF) — ExpoTech 2026.2**
> *Disciplinas integradas: Computational Intelligence & Algorithm Optimization • Telecom & Security • Architecture & Patterns • Open Source*

---

## 💡 1. O Problema que Resolvemos (Em Linguagem Simples)

Aparelhos inteligentes de baixo custo costumam vir de fábrica com falhas graves de segurança: senhas padrão (`admin:admin123`), falta de criptografia e portas antigas abertas (como a porta `23` do protocolo **Telnet**). Um morador comum não sabe usar ferramentas técnicas de rede para descobrir se um aparelho da sua casa está vulnerável ou sofrendo um ataque.

Ao mesmo tempo, criar uma regra fixa no computador para dar uma "nota de perigo" aos aparelhos é difícil: **qual pista de rede importa mais?** Uma porta insegura aberta? Um volume estranho de dados? Um aparelho novo que acabou de entrar no Wi-Fi?

O **HomeGuard** resolve esses dois problemas de ponta a ponta:
1. **Na ponta da rede:** Escuta os pacotes que passam pelo ambiente e extrai **5 pistas (*features*)** de cada aparelho.
2. **No cérebro do sistema (PSO):** Usa um algoritmo bioinspirado de **Enxame de Partículas** para descobrir matematicamente **qual é o peso ideal de cada pista**, sem depender de "chutes" manuais.
3. **Na tela do morador:** Mostra uma planta baixa da casa (**Casa Virtual**) onde aparelhos seguros ficam verdes e aparelhos perigosos piscam em vermelho, com um botão **"Mitigar"** para bloquear a ameaça na hora.

---

## 🔗 2. Como Tudo se Conecta (Fluxo Ponta a Ponta)

O diagrama abaixo mostra o caminho completo que a informação percorre dentro do projeto, desde o microcontrolador até a tela do usuário:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ 1. DISPOSITIVOS IoT (Físicos no ESP32 ou Simulados via Container)            │
│    • ESP32 "A" (Normal): Envia temperatura a cada 5s via MQTT (porta 1883)   │
│    • ESP32 "B" (Vulnerável): Abre porta Telnet (23) vazando admin:admin123   │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │ Pacotes TCP / UDP trafegando na rede
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ 2. CAPTURA E EXTRAÇÃO DE PISTAS (backend/app/capture + domain/analyzers)     │
│    • TShark / PyShark captura os pacotes da rede ou de arquivos .pcap        │
│    • AnalyzerFactory escolhe TcpAnalyzer ou UdpAnalyzer (Padrão Strategy)    │
│    • Extrai 5 features normalizadas (de 0.0 a 1.0) em janelas de 30 segundos │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │ Vetor de 5 features do aparelho
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ 3. MOTOR DE INTELIGÊNCIA COMPUTACIONAL — PSO (backend/app/domain/pso)        │
│    • Multiplica as 5 features pelos 5 pesos ótimos aprendidos pelo enxame    │
│    • Calcula o Score de Risco (0.0 a 1.0) e classifica:                      │
│      🟢 Normal (< 0.30)   |   🟡 Atenção (0.30 a 0.69)   |   🔴 Risco (≥ 0.70)│
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │ Salva no SQLite e dispara evento
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ 4. API REST, BANCO DE DADOS E WEBSOCKET (backend/app/api + infra)            │
│    • Salva dispositivos e alertas no banco SQLite via SQLAlchemy             │
│    • Envia alerta instantâneo via WebSocket (/ws/alerts) sem precisar F5     │
└──────────────────┬───────────────────────────────────────▲───────────────────┘
                   │ Atualiza tela em < 50ms               │ Usuário clica em "Mitigar"
                   ▼                                       │ (POST /devices/{id}/mitigate)
┌──────────────────────────────────────────────────────────┴───────────────────┐
│ 5. DASHBOARD WEB INTERATIVO (frontend/ — React + Vite)                       │
│    • Aba "Casa Virtual": Planta baixa da casa + Cartões + Simulador do PSO   │
│    • Aba "Análise de risco": Gráficos estatísticos da rede                   │
│    • Aba "Mitigações": Histórico auditável de bloqueios realizados           │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🧩 3. Explicação Didática de Cada Componente (Como Foi Elaborado)

Para manter o projeto organizado e fácil de manter, construímos um **monólito modular** dividido em componentes com responsabilidades únicas:

### 3.1. Hardware e Firmware (`firmware/` e `infra/simulator/`)
Criamos dois perfis de dispositivos IoT para provar que o sistema diferencia um aparelho legítimo de um aparelho perigoso:
- **ESP32 "A" — Sensor Confiável (`firmware/esp_normal/`):** Escrito em C/C++ (PlatformIO). Publica leituras de temperatura a cada 5 segundos no tópico MQTT `homeguard/sensores/temperatura` (porta `1883`). Foi construído com boas práticas de sistemas embarcados: temporização não-bloqueante (`millis()` em vez de `delay()`), variação aleatória (*jitter*) e reconexão automática com *backoff* exponencial.
- **ESP32 "B" — Dispositivo Vulnerável (`firmware/esp_vulneravel/`):** Simula um aparelho mal configurado de fábrica. Abre a porta TCP `23` (**Telnet**, que não tem criptografia) e transmite usuário e senha (`admin:admin123`) em texto puro para quem conectar. Representa a falha real catalogada como **CWE-319** (*Cleartext Transmission of Sensitive Information*) e a técnica **MITRE ATT&CK T1040** (*Network Sniffing*).
- **Simulador em Python (`infra/simulator/sim_esp.py`):** Como nem sempre a banca avaliadora tem as placas ESP32 físicas em mãos, criamos este simulador em software que roda dentro do Docker e gera exatamente o mesmo tráfego MQTT e Telnet na rede virtual.

---

### 3.2. Captura de Rede e Analisadores de Protocolo (`backend/app/capture/` e `domain/analyzers/`)
- **Como funciona:** O módulo `capture/` usa a biblioteca `pyshark` (integrada ao **TShark/Wireshark**) para ler pacotes ao vivo da placa de rede (`live_capture.py`) ou de arquivos gravados `.pcap` (`file_capture.py`).
- **Como foi elaborado (Padrões *Strategy* e *Factory*):**
  Em vez de criar um código cheio de `if/else` para verificar se o pacote é TCP ou UDP, aplicamos dois padrões clássicos de engenharia de software:
  - **Strategy (`base.py`, `tcp_analyzer.py`, `udp_analyzer.py`):** Cada protocolo tem sua própria classe especialista que sabe extrair dados daquele tipo de pacote (ex: o `TcpAnalyzer` verifica se a porta de destino é `23`, `21` ou `80`; o `UdpAnalyzer` verifica tráfego na porta `1883`).
  - **Factory (`factory.py` e `pipeline.py`):** A classe `AnalyzerFactory` recebe o pacote bruto, entrega para o analisador correto e descarta com segurança pacotes sem camada de transporte (como ARP ou ICMP), contabilizando tudo.

---

### 3.3. O Cérebro do Projeto: Algoritmo PSO (`backend/app/domain/pso/`)
Este componente responde à pergunta central da disciplina de *Computational Intelligence & Algorithm Optimization*: **como calibrar automaticamente o cálculo de risco?**

#### As 5 Pistas (*Features*) Observadas em Cada Dispositivo
A cada janela de 30 segundos, resumimos o comportamento de cada aparelho em 5 números de `0.0` a `1.0`:
1. **`taxa_pacotes_suspeitos` (`0.0` a `1.0`):** Porcentagem de pacotes daquele aparelho indo para portas inseguras (`23`, `21`, `80`).
2. **`uso_porta_insegura` (`0` ou `1`):** Vale `1` se o aparelho usou Telnet/FTP sem criptografia, ou `0` se não usou.
3. **`volume_anomalo` (`0.0` a `1.0`):** Quanto o volume de bytes fugiu do histórico normal daquele aparelho.
4. **`dispositivo_desconhecido` (`0` ou `1`):** Vale `1` se o endereço MAC do aparelho nunca foi visto antes na casa.
5. **`frequencia_conexoes` (`0.0` a `1.0`):** Quantidade de novas conexões abertas por minuto (detecta varreduras).

#### A Modelagem Matemática da Otimização
- **Variáveis de Decisão:** O vetor de 5 pesos $\vec{w} = [w_1, w_2, w_3, w_4, w_5]$, onde cada peso define a importância de uma pista.
- **Restrições:** Cada peso deve ficar estritamente entre `0.0` e `1.0` ($w_i \in [0, 1]$), e a soma dos pesos não pode zerar a divisão.
- **Cálculo do Score de Risco (`modelo.py`):** É a média ponderada das 5 pistas dividida pela soma dos pesos:
  $$\text{Score}(\vec{w}, \vec{F}) = \frac{w_1 F_1 + w_2 F_2 + w_3 F_3 + w_4 F_4 + w_5 F_5}{w_1 + w_2 + w_3 + w_4 + w_5}$$
- **Função Objetivo / Fitness (`otimizador.py`):** Minimizar o **Erro Quadrático Médio (MSE)** entre a nota calculada pela fórmula e o risco real conhecido em um conjunto de dados rotulado (`dataset.py`, com 180 janelas de tráfego divididas em 70% treino e 30% teste cego).

#### Como o Enxame de Partículas (PSO) Funciona Aqui?
Implementamos o PSO **do zero usando apenas NumPy** (`otimizador.py`):
1. Criamos um enxame com **30 partículas** (cada partícula é um "palpite" com 5 pesos sorteados entre `0` e `1`).
2. Durante **100 iterações**, cada partícula testa seu palpite no conjunto de treino e ajusta sua velocidade combinando:
   - Sua inércia atual ($w = 0.9$),
   - O melhor lugar que **ela mesma** já visitou ($pBest$, peso $c_1 = 0.5$),
   - O melhor lugar que **o bando inteiro** já encontrou ($gBest$, peso $c_2 = 0.3$).
3. **O que o PSO descobriu sozinho (`pesos_treinados.json`):**
   - Deu importância máxima para **`taxa_pacotes_suspeitos` (`1.000`)** e alta para **`volume_anomalo` (`0.669`)** e **`frequencia_conexoes` (`0.522`)**.
   - **Zerou o peso de `dispositivo_desconhecido` (`0.000`)!** Isso acontece porque um aparelho novo entrar na rede, por si só, não significa ataque — se déssemos peso fixo para isso, geraríamos alarmes falsos ou diluiríamos a nota de aparelhos antigos que foram invadidos.

#### Comparação Científica contra Baselines (30 Execuções Independentes)
Para provar que o PSO realmente melhora o sistema, o script `backend/scripts/avaliar_baseline_pso.py` roda o PSO **30 vezes com sementes aleatórias diferentes (1 a 30)** e compara contra dois Baselines no conjunto de teste cego:

| Métrica no Conjunto de Teste | Baseline 1: Pesos Iguais (`[0.2]*5`) | Baseline 2: Heurística Gulosa (Porta/Suspeitos) | **Nosso PSO (30 rodadas: Média ± Desvio)** |
|---|---|---|---|
| **Erro MSE (quanto menor, melhor)** | `0.01880` | `0.04170` | **`0.01286 ± 0.00000`** *(-31,6% de erro)* |
| **Acurácia Global** | `80.0%` | `72.7%` | **`90.9% ± 0.00%`** |
| **F1-Score Macro (Equilíbrio Geral)** | `80.2%` | `67.3%` | **`90.7% ± 0.00%`** *(+10,5 pontos)* |
| **Detecção de Risco Crítico (Recall)** | `70.0%` *(perde 30% dos ataques!)* | `100.0%` *(mas erra a classe Atenção)* | **`95.0% ± 0.00%`** |
| **Taxa de Falso Positivo (Normal)** | `0.0%` | `0.0%` | **`0.0% ± 0.00%`** *(zero alarme falso)* |

> **Separação Arquitetural Importante:** O arquivo `modelo.py` (que calcula a nota na hora em que o sistema está rodando) é 100% separado do `otimizador.py` (que treina os pesos). Além disso, o servidor web **não re-treina o PSO a cada pacote** — ele lê os pesos já salvos em `pesos_treinados.json` para responder instantaneamente, e só roda um novo treino se o usuário pedir na tela (`POST /pso/treinar`).

---

### 3.4. API REST, Banco de Dados e Mitigação (`backend/app/api/`, `infra/` e `domain/mitigacao.py`)
- **API FastAPI (`routes.py` e `routes_pso.py`):** Criada seguindo o modelo *API-First*, gerando documentação automática no Swagger (`/docs`). Entrega a lista de aparelhos (`GET /devices`), alertas (`GET /alerts`), dados do PSO (`GET /pso/pesos`, `POST /pso/treinar`, `POST /pso/simular`) e recebe ordens de bloqueio (`POST /devices/{id}/mitigate`).
- **Tempo Real com WebSocket (`ws_manager.py` — Padrão *Observer*):** Mantém um canal aberto (`/ws/alerts`) com todos os navegadores conectados. Assim que um alerta ou mitigação ocorre, o backend avisa todos os clientes instantaneamente sem precisar recarregar a página.
- **Banco de Dados (`database.py`, `models.py`, `repositorio.py`):** Usa **SQLite** com **SQLAlchemy**, isolando toda a leitura e gravação dentro da camada `infra/`.
- **Mitigação Segura e Auditável (`mitigacao.py`):** Quando o usuário clica em **"Mitigar"** no painel, o backend valida rigorosamente o endereço IP (usando a biblioteca `ipaddress`) e a porta (`1..65535`). Por questão de segurança e para funcionar igual em Windows, Mac e Linux, o bloqueio opera em **Modo Simulado Auditável**: registra a ação nos logs de auditoria, cria um alerta de mitigação no banco e notifica a tela em tempo real.

---

### 3.5. Frontend: A "Casa Virtual" (`frontend/`)
Construído em **React 19 + Vite** com gráficos em **Recharts**, o painel foi desenhado para ser entendido tanto por um morador leigo quanto pela banca avaliadora. Possui 3 abas principais:
1. **Aba "Casa Virtual":**
   - **Planta Baixa (`HouseMap.jsx`):** Desenha os cômodos da casa e posiciona cada aparelho com a cor do seu risco atual (verde, amarelo ou vermelho pulsante).
   - **Feed de Alertas e Cartões (`AlertFeed.jsx` e `DeviceCard.jsx`):** Mostra IP, endereço MAC, barra de score e o botão **"Mitigar"**.
   - **Painel do Motor PSO (`PsoPanel.jsx`):** Exibe a curva de convergência das 100 iterações, o gráfico de barras dos 5 pesos aprendidos, a matriz de confusão e um **Simulador Interativo** onde é possível arrastar barrinhas com as 5 pistas para ver a nota de risco mudar ao vivo.
2. **Aba "Análise de risco" (`AnalisePage.jsx`):** Gráficos de distribuição de risco e histórico da rede.
3. **Aba "Mitigações" (`MitigacoesPage.jsx`):** Tabela completa com o histórico de bloqueios aplicados, horário e justificativa.

---

### 3.6. Infraestrutura e Automação (`infra/`, `.github/workflows/`, `hg.cmd`)
- **Docker Compose (`infra/docker-compose.yml`):** Sobe 5 serviços integrados com um único comando: `mosquitto` (broker MQTT), `esp-sim` (simulador dos ESPs), `backend` (FastAPI), `web` (React + Nginx) e `caddy` (proxy reverso que unifica tudo na porta `8080`).
- **CI/CD (`ci.yml` e `firmware-ci.yml`):** Toda vez que alguém abre um Pull Request no GitHub, os robôs rodam automaticamente o linter (`flake8` e `eslint`) e todas as baterias de testes do backend, frontend e firmware.

---

## 🚀 4. Como Executar o Projeto Localmente

### Opção 1: Via Docker Desktop (Recomendada — Sobe Tudo em 1 Comando)

Com o **Docker Desktop** aberto no computador, abra o terminal na raiz do projeto e execute:

```powershell
# 1. Sobe toda a pilha (Mosquitto + Simulador ESPs + Backend + Frontend + Caddy):
.\hg.cmd sim

# 2. Verifica se todos os serviços (API, MQTT e Telnet) estão saudáveis:
.\hg.cmd check

# 3. (Opcional) Acompanhar os logs em tempo real:
.\hg.cmd logs backend
.\hg.cmd logs esp-sim

# 4. Para encerrar e desligar os contêineres:
.\hg.cmd down

# 5. Se precisar zerar o banco de dados para uma nova apresentação:
.\hg.cmd reset
```

- **Dashboard Web (Casa Virtual):** [http://localhost:8080](http://localhost:8080)
- **Documentação da API (Swagger):** [http://localhost:8080/api/docs](http://localhost:8080/api/docs)
- **Porta Telnet do Simulador Vulnerável:** `localhost:2323`

---

### Opção 2: Rodando Nativamente no Windows (Sem Docker)

Caso prefira rodar cada parte direto no sistema operacional (requer **Python 3.11+** e **Node.js 20+**):

#### Passo 1 — Subir o Backend (Terminal 1)
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Habilita os dispositivos iniciais de demonstração no banco SQLite:
$env:CARREGAR_DADOS_INICIAIS="true"

# Inicia a API na porta 8000:
uvicorn app.main:app --reload --port 8000
```
> API disponível em [http://localhost:8000](http://localhost:8000) (Swagger em [http://localhost:8000/docs](http://localhost:8000/docs)).

#### Passo 2 — Subir o Frontend (Terminal 2)
```powershell
cd frontend
npm install
npm run dev
```
> Dashboard disponível em [http://localhost:5173](http://localhost:5173).

#### Passo 3 — Rodar o Simulador de ESPs (Opcional — Terminal 3)
```powershell
$env:TELNET_PORT="2323"
python infra/simulator/sim_esp.py
```

---

## 🧪 5. Como Rodar os Testes e o Comparativo do PSO

### Comparativo Científico: PSO (30 execuções) vs. Baselines
Para exibir na tela a tabela comparativa exigida pelo edital (com média, desvio-padrão, MSE, MAE, Precisão, Recall, F1 e Falso Positivo):
```powershell
.\backend\venv\Scripts\python.exe backend/scripts/avaliar_baseline_pso.py
```

### Testes Automatizados do Backend (Python / pytest)
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest tests/ -v
```

### Testes Automatizados do Frontend (React / Vitest)
```powershell
cd frontend
npm test -- --run
```

### Testes Unitários do Firmware (C / PlatformIO Unity)
```powershell
cd firmware
pio test -e native
```

---

## 🔄 6. Dica para a Apresentação: Como Resetar o Botão "Mitigar"

Durante os ensaios, ao clicar em **"Mitigar"**, o navegador guarda no `localStorage` que aquele aparelho já foi mitigado. Para deixar o botão ativo novamente antes de apresentar para a banca:

1. No navegador, pressione **`F12`** para abrir o *DevTools*.
2. Na aba **Console**, digite o comando abaixo e aperte **Enter**:
   ```javascript
   localStorage.clear();
   location.reload();
   ```

---

## 📁 7. Mapa de Pastas do Repositório

```text
HomeGuard/
├── backend/                        # Servidor Python (FastAPI + SQLite + PSO)
│   ├── app/
│   │   ├── api/                    # Rotas REST (/devices, /alerts, /pso) e WebSocket
│   │   ├── capture/                # Captura de pacotes com PyShark (ao vivo e .pcap)
│   │   ├── domain/
│   │   │   ├── analyzers/          # Padrões Strategy e Factory para pacotes TCP/UDP
│   │   │   ├── pso/                # Motor PSO (modelo, otimizador NumPy, dataset e métricas)
│   │   │   ├── mitigacao.py        # Validação de IP/porta e bloqueio simulado auditável
│   │   │   └── pipeline.py         # Orquestrador que transforma pacotes em features
│   │   └── infra/                  # Banco SQLite, modelos SQLAlchemy e dados iniciais
│   ├── scripts/                    # Scripts de treino do PSO e avaliação contra Baselines
│   └── tests/                      # Suíte de testes automatizados com pytest
├── frontend/                       # Painel Web em React 19 + Vite + Recharts
│   └── src/
│       ├── components/             # Casa Virtual (HouseMap), PsoPanel, DeviceCard, AlertFeed
│       ├── hooks/                  # Hook useHomeGuard (integra REST + WebSocket)
│       └── services/               # Cliente HTTP, cálculo de risco e dados de fallback
├── firmware/                       # Código C/C++ dos microcontroladores ESP32
│   ├── esp_normal/                 # ESP32 "A" — Sensor de temperatura via MQTT
│   ├── esp_vulneravel/             # ESP32 "B" — Servidor Telnet vulnerável (porta 23)
│   ├── lib/homeguard_core/         # Funções puras em C compartilhadas (backoff, jitter, etc.)
│   └── test/test_core/             # Testes unitários nativos em C (Unity)
├── infra/                          # Docker Compose, proxy Caddy, Mosquitto e simulador Python
├── docs/                           # Documentação detalhada de arquitetura e decisões (00 a 07)
└── hg.cmd / hg.sh                  # Utilitário de linha de comando para subir e testar tudo
```
