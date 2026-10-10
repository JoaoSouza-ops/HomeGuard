# HomeGuard

Sistema open source de monitoramento e classificação de risco para redes domésticas com dispositivos IoT. Captura tráfego de rede, classifica o risco de cada dispositivo usando **PSO (Particle Swarm Optimization)** e exibe tudo em um dashboard web em tempo real.

Projeto acadêmico — NEXUS (6º-8º semestre, Engenharia da Computação) — ExpoTech 2026.2.

## ⚠️ Antes de começar: leia isto

Este projeto assume um conjunto de decisões técnicas. Antes de qualquer linha de código, **toda a equipe precisa ler e confirmar** [`docs/00-PREMISSAS.md`](docs/00-PREMISSAS.md). Ele lista o que já está decidido e o que ainda precisa ser validado (quantidade de placas ESP disponíveis, isolamento de rede, etc). Não pule essa etapa — vários dos guias abaixo dependem dessas respostas.

## O que é o HomeGuard

- Dois (ou mais) microcontroladores **ESP32/ESP8266** simulam dispositivos IoT em uma rede de testes: um com tráfego normal (MQTT/HTTP) e outro com uma vulnerabilidade real proposital (servidor Telnet aberto, sem criptografia).
- Um backend em **Python + FastAPI** captura o tráfego dessa rede (via `pyshark`/TShark), extrai características de cada fluxo e envia para o motor de classificação.
- O motor de **PSO** otimiza um score de risco por dispositivo e classifica em `Normal`, `Atenção` ou `Risco`.
- Um frontend em **React** ("Casa Virtual") mostra os dispositivos, o score de risco em tempo real e permite disparar a mitigação (bloqueio da porta/IP).
- Tudo containerizado com **Docker Compose**, com CI/CD no **GitHub Actions** e deploy final na **AWS**.

## Estrutura do repositório

```
homeguard/
├── firmware/          # Código dos ESP32/ESP8266 (Arduino/PlatformIO)
├── backend/           # API FastAPI + captura de tráfego + motor PSO
├── frontend/          # Dashboard React ("Casa Virtual")
├── infra/             # Docker Compose, GitHub Actions, scripts de deploy AWS
├── docs/              # Toda a documentação técnica (este diretório)
├── CONTRIBUTING.md
└── README.md          # este arquivo
```

## Documentação completa

Leiam nesta ordem:

1. [`docs/00-PREMISSAS.md`](docs/00-PREMISSAS.md) — **leitura obrigatória antes de tudo**
2. [`docs/01-ARQUITETURA.md`](docs/01-ARQUITETURA.md) — visão geral do sistema, padrões de projeto
3. [`docs/02-REDE-HARDWARE.md`](docs/02-REDE-HARDWARE.md) — setup dos ESP32/ESP8266 e captura de tráfego
4. [`docs/03-BACKEND-API.md`](docs/03-BACKEND-API.md) — contrato da API (OpenAPI), estrutura do backend
5. [`docs/04-ALGORITMO-PSO.md`](docs/04-ALGORITMO-PSO.md) — a matemática e a implementação do PSO
6. [`docs/05-FRONTEND.md`](docs/05-FRONTEND.md) — estrutura do dashboard React
7. [`docs/06-SEGURANCA.md`](docs/06-SEGURANCA.md) — a vulnerabilidade proposital e como mitigá-la
8. [`docs/07-DEVOPS-CLOUD.md`](docs/07-DEVOPS-CLOUD.md) — Docker, CI/CD e deploy na AWS
9. [`docs/08-CRONOGRAMA-PAPEIS.md`](docs/08-CRONOGRAMA-PAPEIS.md) — cronograma de 8 semanas e divisão de papéis
10. [`CONTRIBUTING.md`](CONTRIBUTING.md) — fluxo de Git e regras de contribuição

## Quick start (depois que o backend e o frontend existirem)

```bash
git clone <url-do-repo>
cd homeguard
cp .env.example .env        # ajustar credenciais/IPs conforme docs/00-PREMISSAS.md
docker compose up --build
```

- API: `http://localhost:8000/docs` (Swagger gerado automaticamente pelo FastAPI)
- Dashboard: `http://localhost:3000`

## Stack confirmada

| Camada | Tecnologia |
|---|---|
| Firmware | ESP32/ESP8266, Arduino Framework (ou PlatformIO) |
| Captura de rede | TShark + `pyshark` |
| Backend/API | Python 3.11 + FastAPI |
| Inteligência computacional | PSO implementado em Python (`pyswarms` ou implementação própria) |
| Frontend | React (SPA separada) |
| Mensageria IoT | MQTT (Eclipse Mosquitto) |
| Containerização | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Cloud | AWS (EC2) |
| Testes | pytest (backend), Jest/React Testing Library (frontend) |
| Versionamento | Git + Conventional Commits |
