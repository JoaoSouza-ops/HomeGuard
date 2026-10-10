# 06 — Segurança: Vulnerabilidade Real e Mitigação

Este documento cobre o requisito do edital: **"ao menos uma vulnerabilidade real identificada e mitigada"**.

## 1. Regra de ouro

> **Tudo neste documento só pode ser executado na rede de testes isolada definida em `docs/00-PREMISSAS.md` (item 2) e `docs/02-REDE-HARDWARE.md`.** Rodar serviços vulneráveis de propósito fora desse ambiente controlado é uma prática de risco real, independentemente de ser um projeto acadêmico.

## 2. A vulnerabilidade escolhida: serviço Telnet exposto com credenciais fracas

### Por que essa vulnerabilidade é real e relevante
- Telnet transmite usuário e senha **em texto puro**, sem nenhuma criptografia — qualquer um capturando o tráfego da rede consegue ler a senha.
- É uma das causas raiz mais documentadas de comprometimento de dispositivos IoT reais (routers, câmeras, DVRs) — inclusive é a porta de entrada clássica de botnets como a família Mirai.
- Mapeamento de referência (para citar na apresentação): isso corresponde à técnica **T1040 (Network Sniffing)** e à fraqueza **CWE-319 (Cleartext Transmission of Sensitive Information)** em catálogos usados pela indústria (MITRE ATT&CK / CWE).

### Como reproduzir no laboratório
Já implementado no ESP "B" (`docs/02-REDE-HARDWARE.md`, seção 3): ele abre a porta 23 e "vaza" um usuário/senha fixos para qualquer conexão.

## 3. Identificação (detecção)

A identificação acontece em duas camadas:

1. **Captura de rede**: o `TcpAnalyzer` (docs/01-ARQUITETURA.md) marca qualquer pacote destinado à porta 23 como `is_insecure_port = True`.
2. **Classificação de risco**: essa feature entra no cálculo do PSO (docs/04) com peso alto, empurrando o score do dispositivo para a faixa "Risco".

Evidência que a equipe deve capturar para a apresentação:
- Print/gravação do `tshark` mostrando o pacote na porta 23 com o payload legível (usuário/senha visíveis).
- Print do dashboard mostrando o dispositivo classificado como "Risco" com o motivo do alerta.

## 4. Mitigação

Duas estratégias, do mais simples ao mais completo — recomendamos implementar pelo menos as duas primeiras:

### Nível 1 — Bloqueio de porta via regra de firewall local
No computador/servidor que roda o backend (ou no roteador de testes, se ele suportar):
```bash
# Linux (iptables) - bloqueia qualquer tráfego para a porta 23 vindo do IP do ESP vulnerável
sudo iptables -A FORWARD -s <IP_DO_ESP_VULNERAVEL> -p tcp --dport 23 -j DROP
```

### Nível 2 — Ação automatizada pelo próprio HomeGuard
O endpoint `POST /devices/{device_id}/mitigate` (docs/03-BACKEND-API.md) deve, ao receber `acao: "bloquear_porta"`, executar o bloqueio programaticamente:

```python
# app/domain/mitigacao.py
import subprocess

def bloquear_porta(ip: str, porta: int):
    comando = ["sudo", "iptables", "-A", "FORWARD", "-s", ip, "-p", "tcp", "--dport", str(porta), "-j", "DROP"]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    if resultado.returncode != 0:
        raise RuntimeError(f"Falha ao bloquear porta: {resultado.stderr}")
```

> ⚠️ Executar comandos de sistema a partir da API é sensível. Para o escopo do projeto está OK (ambiente de laboratório controlado, TCC/expo), mas documentem claramente essa limitação: **em um cenário de produção real, isso exigiria validação de permissões, autenticação forte no endpoint e um usuário de sistema com privilégios mínimos**, não `sudo` livre.

### Nível 3 (opcional, ganha pontos extras) — Correção na origem
Trocar o firmware do ESP "vulnerável" para não usar mais Telnet, e sim um protocolo com autenticação e criptografia (ex: MQTT com TLS na porta 8883), demonstrando o "antes x depois" ao vivo na apresentação.

## 5. Roteiro de demonstração sugerido para a banca

1. Mostrar o dashboard com o ESP "B" classificado como "Risco".
2. Mostrar a captura de pacotes evidenciando a porta 23 aberta.
3. Clicar em "Mitigar" no dashboard.
4. Mostrar, ao vivo, que uma nova tentativa de conexão Telnet ao IP do ESP falha (`Connection refused` ou timeout).
5. Mostrar o dashboard atualizando o status do dispositivo (via WebSocket, sem dar refresh).

## 6. Checklist de segurança responsável

- [ ] A rede de testes está isolada da internet e de outros dispositivos durante os testes.
- [ ] As credenciais fracas usadas são fictícias, nunca reaproveitadas de contas reais de qualquer integrante.
- [ ] Nenhum print/vídeo da apresentação expõe IPs ou redes de terceiros.
- [ ] O código de mitigação nunca é executado contra hosts fora da rede de testes.
