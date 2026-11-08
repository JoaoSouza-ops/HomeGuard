# Como rodar o HomeGuard (todo o grupo)

Você só precisa de **Git** e **Docker Desktop** (aberto, com "Engine running"). Não precisa instalar Python, Node nem ter o Arduino/ESP.

## Rodar em 3 comandos

```powershell
git clone https://github.com/JoaoSouza-ops/HomeGuard.git C:\homeguard
cd C:\homeguard
.\hg.cmd sim
```
(Linux/macOS/Git Bash: `./hg.sh sim`.)

A primeira vez demora uns minutos (baixa imagens). Depois abra:

| O quê | Endereço |
|---|---|
| Dashboard | http://localhost:8080 |
| API (Swagger) | http://localhost:8080/api/docs |

O `hg` cria o `.env` sozinho na primeira execução. Não precisa editar nada.

## Comandos

| Comando | O que faz |
|---|---|
| `.\hg.cmd sim` | Sobe tudo **com o simulador dos ESPs** (testar sem hardware) |
| `.\hg.cmd up` | Sobe tudo **sem** simulador (use quando os ESPs reais estiverem ligados) |
| `.\hg.cmd check` | Testa API, broker MQTT e Telnet (3 testes) |
| `.\hg.cmd ps` | Mostra o estado dos serviços |
| `.\hg.cmd logs backend` | Acompanha os logs de um serviço (Ctrl+C sai) |
| `.\hg.cmd down` | Para tudo |
| `.\hg.cmd reset` | Para tudo e **apaga os dados** (banco SQLite) |

## Testar sem o Arduino (simulador)

`.\hg.cmd sim` liga um container que imita o firmware:
- **ESP "A"**: publica uma temperatura (ex.: `21.30`) a cada 5 s no tópico `homeguard/sensores/temperatura` (mesmo tópico, formato e client id do firmware).
- **ESP "B"**: abre a porta 23 e responde `login: admin / password: admin123` em texto puro (credenciais fictícias).

Para ver as mensagens chegando:
```powershell
cd infra
docker compose --env-file ../.env --profile lab --profile sim exec mosquitto mosquitto_sub -t "homeguard/#" -v
```
Para testar o Telnet: `telnet localhost 2323`.

`.\hg.cmd check` roda os 3 testes e diz `[ OK ]` ou `[FALHA]` para cada um.

## Trocar o simulador pelo hardware de verdade
1. Desligue o simulador: `.\hg.cmd down` e depois `.\hg.cmd up`.
2. Redes/Hardware: coloque o IP do notebook (`ipconfig`) em `HG_MQTT_BROKER_IP` no `secrets.h` do ESP "A" e libere a porta no firewall (PowerShell como administrador):
   `New-NetFirewallRule -DisplayName "HomeGuard MQTT" -Direction Inbound -Protocol TCP -LocalPort 1883 -Action Allow -Profile Private`
3. `.\hg.cmd check` deve continuar com MQTT `[ OK ]`, agora vindo da placa. Para testar o Telnet do ESP "B" real: `docker compose ... run --rm -e TELNET_HOST=<IP_DO_ESP_B> esp-sim python check.py` (dentro de `infra/`, com as flags `--env-file ../.env --profile lab --profile sim`).

## Para cada área
- **Backend:** o código fica em `backend/` e a API sobe em container. Depois de mudar o código, `.\hg.cmd up` recompila. Teste rápido sem Docker: `cd backend; pytest`. A API é publicada em `/api`, então localmente use `http://localhost:8080/api/...`.
- **Frontend:** `frontend/` precisa de `package.json`, `package-lock.json` e scripts `lint` e `test`. A variável `VITE_API_URL` já vale `/api` (mesma origem, sem CORS) e `VITE_WS_URL` vale `ws://localhost:8080/api`. Enquanto não existe frontend, o Docker gera uma página provisória.
- **Captura de pacotes:** roda **fora** do Docker, direto no Windows (Wireshark/tshark + Npcap), apontando para `http://localhost:8080/api`.

## Problemas comuns
| Sintoma | Solução |
|---|---|
| `docker: command not found` / erro de conexão | Abra o Docker Desktop e espere ficar verde |
| Porta 8080 ocupada | Mude `HTTP_PORT` no `.env` e rode `.\hg.cmd up` de novo |
| `.\hg.cmd` bloqueado | Use `cmd /c hg.cmd sim` |
| Mudei o código e nada mudou | `.\hg.cmd up` recompila; se persistir, `.\hg.cmd down` e `up` |
| `check` falha só no MQTT | Rode `.\hg.cmd sim` (sem simulador não chega mensagem) |
