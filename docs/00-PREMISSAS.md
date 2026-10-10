# 00 — Premissas do Projeto

Este documento existe para que **nada seja assumido silenciosamente**. Ele tem duas partes: o que já está **confirmado pela equipe** e o que ainda está **pendente de confirmação**. Antes de começar a codar, reúnam a equipe, revisem a seção "Pendente" e marquem cada item como decidido.

## ✅ Confirmado pela equipe

| Decisão | Valor |
|---|---|
| Framework de backend | **FastAPI** |
| Abordagem de frontend | **React (SPA separada, consumindo a API via HTTP/WebSocket)** |
| Provedor de nuvem | **AWS** |
| Tamanho da equipe | 5 pessoas |
| Prazo de entrega | até **01/11/2026** (8 semanas a partir de 08/09/2026) |
| Hardware de teste | ESP32/ESP8266 físicos simulando dispositivos IoT (não só tráfego simulado por software) |
| Fluxo de Git | GitHub Flow (branch curta → PR → code review → merge em `main`) |
| Padrão de commits | Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `test:`) |
| Testes de backend | `pytest` |
| Broker MQTT | Eclipse Mosquitto |
| Orquestração local | Docker Compose (sem Kubernetes) |
| Captura de pacotes | `pyshark` (wrapper Python do TShark) |

## ❗ Pendente — a equipe precisa decidir isto ANTES da Semana 1

Cada um destes itens muda diretamente as instruções técnicas dos outros documentos. Preencham a coluna "Decisão da equipe" e distribuam a atualização nos documentos referenciados.

| # | Pergunta | Por que importa | Onde impacta | Decisão da equipe |
|---|---|---|---|---|
| 1 | Quantas placas ESP32/ESP8266 vocês têm disponíveis? (mínimo recomendado: 2 — uma "normal", uma "vulnerável") | Define quantos tipos de dispositivo o dashboard vai exibir e quão rico fica o cenário de demonstração | `02-REDE-HARDWARE.md` | _____ |
| 2 | A rede de testes será um roteador/AP **dedicado e isolado** (recomendado por segurança) ou a rede Wi-Fi doméstica/da faculdade de alguém? | Rodar um servidor Telnet vulnerável de propósito em uma rede compartilhada com outros usuários é um risco real. Isso precisa ser isolado. | `02-REDE-HARDWARE.md`, `06-SEGURANCA.md` | _____ |
| 3 | Qual máquina vai rodar o backend/captura de pacotes durante o desenvolvimento? (notebook de um integrante, mini PC, Raspberry Pi?) | Define requisitos de SO e permissões de captura de interface de rede | `02-REDE-HARDWARE.md` | _____ |
| 4 | Alguém da equipe já tem conta AWS criada? É conta pessoal (free tier) ou tem acesso a crédito educacional (AWS Educate/GitHub Student Pack)? | Define limites de instância e se precisamos configurar cobrança/alertas de gasto | `07-DEVOPS-CLOUD.md` | _____ |
| 5 | O repositório será **monorepo** (firmware + backend + frontend + infra juntos, como sugerido neste doc) ou repositórios separados? | Muda os workflows de CI/CD e a estrutura de pastas | `CONTRIBUTING.md`, `07-DEVOPS-CLOUD.md` | _____ |
| 6 | Qual é o nome final do projeto/repositório e a organização/conta no GitHub onde ele será criado? | Necessário para URLs de clone, badges de CI, e para o link que será enviado à coordenação | Todos os documentos | _____ |
| 7 | Vocês vão versionar dados de exemplo (capturas `.pcap` de teste) dentro do repositório ou usar Git LFS / pasta ignorada? | Arquivos `.pcap` podem ficar grandes; isso afeta o `.gitignore` | `02-REDE-HARDWARE.md` | _____ |
| 8 | Persistência de dados: SQLite (mais simples, roda em arquivo) ou Postgres (mais realista, precisa de outro container)? | Muda o `docker-compose.yml` e o código do backend | `03-BACKEND-API.md`, `07-DEVOPS-CLOUD.md` | _____ |

## Como usar este documento

1. Copiem esta tabela para uma call ou reunião presencial da equipe.
2. Preencham a coluna "Decisão da equipe".
3. Qualquer decisão que exija ajuste em outro documento, quem decidiu deve abrir uma issue no GitHub referenciando o arquivo a ser corrigido.
4. Nenhum código de infraestrutura (Docker, CI/CD, deploy) deve começar antes dos itens 4, 5, 6 e 8 estarem resolvidos.
