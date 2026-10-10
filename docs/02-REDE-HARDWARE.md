# 02 — Rede e Hardware (ESP32/ESP8266 + Captura de Tráfego)

**Responsável sugerido:** Especialista de Redes e Hardware (ver `08-CRONOGRAMA-PAPEIS.md`)

> ⚠️ Este documento depende das respostas aos itens 1, 2 e 3 de `00-PREMISSAS.md`. Não montem o ambiente físico antes de confirmar isso com a equipe.

## 1. Conceitos que a pessoa responsável precisa dominar antes de codar

- **Modelo OSI**: foco nas camadas 3 (Rede — IP) e 4 (Transporte — TCP/UDP).
- **Endereçamento IP**: diferença entre IP local (ex: `192.168.x.x`) e IP externo; máscara de sub-rede (ex: `/24`).
- **Protocolos**: TCP (confiável, usado por HTTP e Telnet), UDP (sem confirmação, usado por MQTT em alguns brokers e DNS), ICMP (usado por `ping`).
- **Portas comuns em IoT**: `80` (HTTP), `443` (HTTPS), `23` (Telnet — **inseguro, sem criptografia**), `1883` (MQTT sem TLS), `8883` (MQTT com TLS).

## 2. Montagem do ambiente físico (rede de testes isolada)

**Por que isolar:** o ESP "vulnerável" vai rodar um serviço Telnet propositalmente aberto. Rodar isso na rede Wi-Fi de uma casa cheia de outros dispositivos, ou pior, na rede da faculdade, é um risco real de segurança para terceiros.

Checklist de montagem:
1. Um roteador Wi-Fi dedicado só para o projeto (pode ser um roteador antigo, ou o hotspot de um celular usado exclusivamente para isso).
2. Esse roteador **não deve estar conectado à internet principal da casa/faculdade** durante os testes de vulnerabilidade — só precisa dar IP local via DHCP para os ESPs e para o notebook que roda a captura.
3. Anotem o SSID e a faixa de IP (ex: `192.168.4.0/24`) — vocês vão precisar disso no código de captura.

## 3. Preparando os ESP32/ESP8266

### Ferramentas
- Arduino IDE (mais simples para iniciantes) **ou** PlatformIO (mais profissional, integra com VS Code) — escolham uma e sejam consistentes.
- Cabo USB compatível com a placa.
- Biblioteca `WiFi.h` (nativa do ESP32) ou `ESP8266WiFi.h`.

### ESP "A" — Dispositivo normal (simulação de sensor de temperatura via MQTT)

```cpp
// firmware/esp_normal/esp_normal.ino
#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "NOME_DA_REDE_DE_TESTES";       // confirmar com a equipe
const char* password = "SENHA_DA_REDE";             // confirmar com a equipe
const char* mqtt_server = "192.168.4.10";           // IP do broker Mosquitto (ver docs/07)

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); }
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) {
    client.connect("esp32-sensor-temperatura");
  }
  client.loop();

  float temperatura = 20.0 + random(-20, 20) / 10.0;
  char payload[16];
  dtostrf(temperatura, 4, 2, payload);
  client.publish("homeguard/sensores/temperatura", payload);

  delay(5000);
}
```

### ESP "B" — Dispositivo vulnerável (servidor Telnet aberto)

```cpp
// firmware/esp_vulneravel/esp_vulneravel.ino
#include <WiFi.h>

const char* ssid = "NOME_DA_REDE_DE_TESTES";
const char* password = "SENHA_DA_REDE";

WiFiServer telnetServer(23);  // Porta 23 = Telnet, sem criptografia (a vulnerabilidade)

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); }
  telnetServer.begin();
}

void loop() {
  WiFiClient client = telnetServer.available();
  if (client) {
    client.println("login: admin");
    client.println("password: admin123");   // senha fraca proposital — ver docs/06-SEGURANCA.md
    client.stop();
  }
}
```

> Anotem o endereço MAC e o IP atribuído por DHCP de cada placa — o backend vai precisar identificar "quem é quem" na rede.

## 4. Capturando o tráfego

### Instalação
```bash
sudo apt install tshark      # Linux
brew install wireshark       # macOS (inclui tshark)
pip install pyshark
```

### Captura ao vivo (para desenvolvimento local)
```python
# backend/app/capture/live_capture.py
import pyshark

def capturar_trafego(interface: str, bpf_filter: str = ""):
    """
    interface: nome da interface de rede (ex: 'wlan0', 'en0')
    bpf_filter: filtro opcional em sintaxe BPF, ex: 'tcp port 23'
    """
    captura = pyshark.LiveCapture(interface=interface, bpf_filter=bpf_filter)
    for pacote in captura.sniff_continuously():
        yield pacote
```

### Captura para arquivo `.pcap` (útil para testes reproduzíveis sem depender do hardware ligado)
```bash
tshark -i wlan0 -w capturas/teste_telnet.pcap -a duration:60
```

```python
# backend/app/capture/file_capture.py
import pyshark

def ler_pcap(caminho_arquivo: str):
    captura = pyshark.FileCapture(caminho_arquivo)
    for pacote in captura:
        yield pacote
```

> **Confirmar (item 7 de `00-PREMISSAS.md`):** arquivos `.pcap` de teste vão para `backend/tests/fixtures/` e devem ser adicionados ao Git normalmente **somente se pequenos (<5MB)**. Arquivos maiores devem ir para `.gitignore` com uma nota no README explicando como gerá-los novamente.

## 5. Testes manuais antes de integrar com o backend

Antes de conectar a captura ao motor PSO, confirmem manualmente:
- [ ] O ESP "A" aparece na rede e publica no tópico MQTT esperado (testem com `mosquitto_sub -t homeguard/sensores/temperatura -h <ip_broker>`).
- [ ] O ESP "B" aceita conexão na porta 23 (testem com `telnet <ip_do_esp_b> 23`).
- [ ] O `tshark`/`pyshark` rodando no notebook consegue enxergar pacotes de ambos os dispositivos (confirmem com `tshark -i <interface>` simples, sem filtro).
