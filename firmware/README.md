# Firmware HomeGuard (ESP32)

Guia para **configurar, gravar e testar** o firmware dos dois ESP32 do projeto. O passo a passo foi validado na prática no Windows com PlatformIO + VS Code.

| Placa | Pasta | O que faz |
|---|---|---|
| ESP "A" — normal | [`esp_normal/`](esp_normal/) | Sensor de temperatura simulado. Publica a cada 5 s no tópico MQTT `homeguard/sensores/temperatura`. **Precisa de um broker MQTT.** |
| ESP "B" — vulnerável | [`esp_vulneravel/`](esp_vulneravel/) | Abre a porta 23 (Telnet) e envia usuário/senha **fictícios** em texto puro. É a vulnerabilidade proposital do projeto. **Não precisa de broker.** |

> ⚠️ **O ESP "B" é inseguro de propósito.** Ligue-o **somente na rede de testes isolada** (`docs/06-SEGURANCA.md`). Nunca use credenciais reais nele.

## Índice

1. [Estrutura](#estrutura)
2. [Pré-requisitos](#1-pré-requisitos)
3. [Preparar o projeto (caminho, VS Code, secrets.h)](#2-preparar-o-projeto)
4. [Compilar e gravar](#3-compilar-e-gravar-na-placa)
5. [**Broker MQTT: qual usar?**](#4-broker-mqtt-qual-usar) ← leia antes de testar o ESP "A"
6. [Verificar se o broker está recebendo](#5-verificar-se-o-broker-está-recebendo)
7. [Testar o ESP "B" (Telnet)](#6-testar-o-esp-b-telnet)
8. [Testes automáticos](#7-testes-automáticos-sem-hardware)
9. [Problemas comuns](#8-problemas-comuns)

## Estrutura

```
firmware/
├── platformio.ini            # só para rodar os testes no PC (env "native")
├── lib/homeguard_core/       # lógica compartilhada (sem Arduino) — é o que os testes cobrem
├── test/test_core/           # testes unitários (Unity)
├── esp_normal/               # projeto PlatformIO do ESP "A"
│   ├── platformio.ini
│   ├── include/secrets.example.h
│   └── src/main.cpp
└── esp_vulneravel/           # projeto PlatformIO do ESP "B"
    ├── platformio.ini
    ├── include/secrets.example.h
    └── src/main.cpp
```

`esp_normal/` e `esp_vulneravel/` são **dois projetos PlatformIO independentes**. Cada um tem o seu `platformio.ini`, e os dois reutilizam `lib/homeguard_core/` (por isso a pasta `firmware/` precisa ficar **inteira**, com `lib/` ao lado dos dois projetos).

## 1. Pré-requisitos

- **VS Code** com a extensão **PlatformIO IDE** (ou só a linha de comando: `pip install platformio`).
- **Placa ESP32 DevKit** (os projetos usam `board = esp32dev`; se a placa for outra, troque essa linha no `platformio.ini`).
- **Cabo USB de dados** (alguns cabos só carregam e a placa não aparece no computador).
- **Driver USB-serial**, conforme o chip da placa (está escrito perto do conector USB):
  - `CP2102`/`CP210x` → driver da Silicon Labs.
  - `CH340`/`CH9102` → driver da WCH.
- **Linux:** adicione seu usuário ao grupo da porta serial e faça logout/login: `sudo usermod -aG dialout $USER`
- **Internet** na primeira compilação: o PlatformIO baixa sozinho o toolchain do ESP32 e a biblioteca `PubSubClient` (algumas centenas de MB, alguns minutos). **Não é preciso instalar nenhuma biblioteca manualmente.**

| Include | De onde vem | Ação |
|---|---|---|
| `Arduino.h`, `WiFi.h` | Plataforma `espressif32` (definida no `platformio.ini`) | Nenhuma, baixa no 1º Build |
| `PubSubClient.h` (só `esp_normal`) | `knolleary/PubSubClient`, listada em `lib_deps` | Nenhuma, baixa no 1º Build |
| `homeguard_core.h` | Pasta local `firmware/lib/homeguard_core/` | Nenhuma, mas a pasta precisa existir |
| `secrets.h` | Arquivo que **você** cria | Ver passo 2.3 |

## 2. Preparar o projeto

### 2.1 Use um caminho simples (importante no Windows)

Coloque a pasta `firmware` em um caminho **sem acentos, sem espaços e fora do OneDrive**, por exemplo:

```
C:\homeguard\firmware
```

Caminhos como `C:\Users\...\OneDrive\Área de Trabalho\...` causam erros do tipo `homeguard_core.h: No such file or directory` / `homeguard_core.c: No such file or directory`, mesmo com os arquivos presentes (o compilador do ESP32 no Windows não lida bem com acentos, e o OneDrive pode deixar arquivos só "na nuvem").

### 2.2 Abra a pasta certa no VS Code

1. `File → Open Folder…`
2. Selecione `C:\homeguard\firmware\esp_normal` (ou `esp_vulneravel`), a pasta que **contém o `platformio.ini`**.
   **Não** abra a raiz do repositório nem a pasta `firmware`, senão o PlatformIO não reconhece o projeto.
3. Se aparecer "Do you trust the authors?", clique em **Yes, I trust**.
4. Espere a barra azul inferior do PlatformIO terminar de carregar.

### 2.3 Crie o `secrets.h`

O `secrets.h` guarda Wi-Fi e IP do broker e **não vai para o Git** (está no `.gitignore`; não o remova de lá).

```bash
cd firmware/esp_normal            # ou esp_vulneravel
cp include/secrets.example.h include/secrets.h
```
No Windows (PowerShell): `Copy-Item include\secrets.example.h include\secrets.h`

Edite `include/secrets.h`:
```c
#define HG_WIFI_SSID "nome-da-rede-de-testes"
#define HG_WIFI_PASSWORD "senha-da-rede"
#define HG_MQTT_BROKER_IP "192.168.0.25"   // só no esp_normal — veja a seção 4
```

- O ESP32 **só conecta em Wi-Fi 2,4 GHz**. Em roteador dual-band, use a rede de 2,4 GHz.
- O ESP e o computador do broker precisam estar **na mesma rede**.
- O `esp_vulneravel` só tem Wi-Fi no `secrets.h` (não usa broker).
- Se esquecer de criar o arquivo, a compilação para com a mensagem `Falta include/secrets.h`.

## 3. Compilar e gravar na placa

1. **Limpe builds antigos:** se existir a pasta `.pio` dentro do projeto, apague-a.
2. **Compile:** clique em **✓ Build** na barra azul inferior, ou rode `pio run` no terminal do VS Code (`Ctrl+'`). Espere `[SUCCESS]`.
3. **Conecte a placa** por USB e confira a porta com `pio device list` (deve aparecer uma `COMx`).
4. **Grave:** clique em **→ Upload**, ou rode `pio run -t upload`.
   - Mais de uma porta? Use `pio run -t upload --upload-port COM5` (troque pelo número certo).
   - Se travar em `Connecting......` ou der `Wrong boot mode`: **segure o botão BOOT** da placa até a gravação começar e solte.
5. **Abra o monitor serial:** ícone da tomada, ou `pio device monitor` (115200). Sair: `Ctrl+C`. Se não aparecer nada, aperte **EN/RESET** na placa. Feche o monitor antes de gravar de novo (ele ocupa a porta).

**O ESP "A" deve mostrar:**
```
[wifi] (re)conectando...
[wifi] conectado, IP 192.168.0.40
[mqtt] conectando ao broker...
[mqtt] conectado
[sensor] publicado: 20.70
```
Se parar em `[mqtt] falhou, rc=-2`, o Wi-Fi está ok e falta o broker: siga a seção 4.

**O ESP "B" deve mostrar:**
```
[wifi] conectado, IP 192.168.0.41
[telnet] servidor vulneravel ouvindo na porta 23
```

Anote o **IP e o MAC** de cada placa: o backend precisa identificar "quem é quem" (`docs/02-REDE-HARDWARE.md`).

## 4. Broker MQTT: qual usar?

O ESP "A" publica para um broker MQTT (Mosquitto). Escolha **um** dos dois caminhos:

| Situação | O que fazer |
|---|---|
| ✅ **A equipe já tem um broker rodando** (Mosquitto do `docker compose` do projeto, de um servidor, de outro integrante) | **Use esse broker.** Coloque o IP dele em `HG_MQTT_BROKER_IP`, grave o ESP e pronto. **Pule a seção 4.2.** |
| ❌ **Ainda não existe broker** | Suba um Mosquitto simples no seu próprio computador, só para teste (seção 4.2). |

> Quando o broker oficial do projeto existir, **troque o IP no `secrets.h` e regrave o ESP**. O broker local abaixo é só um quebra-galho para desenvolver e testar o firmware sem depender dos outros.

### 4.1 Usando o broker da equipe

1. Peça o **IP** do broker (e confirme que a porta é `1883` e que ele aceita conexões sem usuário/senha, já que o firmware atual não usa autenticação).
2. Edite `HG_MQTT_BROKER_IP` no `secrets.h` do `esp_normal` e grave (seção 3).
3. O ESP precisa estar na mesma rede do broker. Siga para a seção 5 para verificar.

### 4.2 Sem broker: Mosquitto simples no seu computador (Windows)

> ⚠️ Use só em rede de testes. A configuração abaixo aceita conexões sem senha.

**a) Instalar.** Baixe o instalador em [mosquitto.org/download](https://mosquitto.org/download/). Pasta padrão: `C:\Program Files\mosquitto`.

**b) Criar o arquivo de configuração** `C:\homeguard\mosquitto.conf` com exatamente:
```
listener 1883 0.0.0.0
allow_anonymous true
```
- **Salve o arquivo antes de iniciar o broker.** (Esquecer disso foi o motivo de o broker ficar só em modo local durante os nossos testes.)
- Confira que o nome é `mosquitto.conf` e não `mosquitto.conf.txt`. Ative "Exibir → Extensões de nomes de arquivos" no Explorador.
- Sem essa configuração, o Mosquitto 2.x só aceita conexões do próprio computador e o ESP não consegue conectar.

**c) Parar o serviço do Mosquitto**, se existir. O instalador costuma registrar um serviço do Windows que sobe com a configuração padrão (só local) e ocupa a porta 1883. No PowerShell **como Administrador**:
```powershell
Get-Service *mosq*           # vê se existe e se está Running
Stop-Service mosquitto       # para o serviço
```

**d) Iniciar o broker com a sua configuração** (deixe a janela aberta, ela mostra o log):
```powershell
& "C:\Program Files\mosquitto\mosquitto.exe" -c C:\homeguard\mosquitto.conf -v
```

**e) Conferir que ele está ouvindo na rede** (em outro PowerShell):
```powershell
netstat -an | findstr 1883
```
| Resultado | Significado |
|---|---|
| `0.0.0.0:1883  LISTENING` | ✅ Correto, aceita conexões da rede |
| `127.0.0.1:1883  LISTENING` | ❌ Só local: o `.conf` não foi lido (não salvo, caminho errado, ou o serviço padrão está rodando) |
| nada | ❌ O broker não está rodando |

**f) Descobrir o IP do computador:** rode `ipconfig` e use o *Endereço IPv4* do adaptador **Wi-Fi** (não Ethernet, VPN, WSL ou Docker). Os três primeiros números precisam ser iguais aos do IP do ESP (ex.: PC `192.168.0.25`, ESP `192.168.0.40`).

**g) Liberar a porta 1883 no firewall.** *Firewall do Windows com Segurança Avançada → Regras de Entrada → Nova Regra → Porta → TCP → 1883 → Permitir a conexão*. Marque o perfil da sua rede: se o Wi-Fi estiver como **Pública**, uma regra só para **Privado** não vale. Alternativa: regra por programa apontando para `mosquitto.exe`.

**h) Colocar o IP no `secrets.h`** (`HG_MQTT_BROKER_IP`) e **regravar** o ESP "A" (seção 3). O ESP reconecta sozinho se o broker subir depois.

> **Linux/macOS:** instale `mosquitto` (`apt install mosquitto mosquitto-clients` / `brew install mosquitto`), use o mesmo `mosquitto.conf` e rode `mosquitto -c mosquitto.conf -v`. O IP vem de `ip a` / `ifconfig`.

## 5. Verificar se o broker está recebendo

Com o ESP "A" ligado, há três formas de confirmar:

1. **Log do broker** (a janela do `mosquitto.exe -v`):
   ```
   New client connected from 192.168.0.40:xxxxx as esp32-sensor-temperatura
   Received PUBLISH from esp32-sensor-temperatura (d0, q0, r0, m0, 'homeguard/sensores/temperatura', ... (5 bytes))
   ```
   Uma linha `Received PUBLISH` a cada 5 segundos.

2. **Assinando o tópico** (mostra o valor das mensagens), em outro terminal:
   ```powershell
   & "C:\Program Files\mosquitto\mosquitto_sub.exe" -h localhost -t "homeguard/#" -v
   ```
   Deve chegar uma linha a cada 5 segundos, com valores entre 18.00 e 22.00:
   ```
   homeguard/sensores/temperatura 20.70
   homeguard/sensores/temperatura 19.40
   ```
   Para ver tudo o que passa pelo broker: `-t "#"`. Em um broker remoto, troque `localhost` pelo IP dele.

3. **Monitor serial do ESP:** `[mqtt] conectado` seguido de `[sensor] publicado: ...` a cada 5 s, sem `falha ao publicar`.

Quando o `mosquitto_sub` mostrar os valores chegando, o teste do ESP "A" está completo (Wi-Fi, broker e publicação).

## 6. Testar o ESP "B" (Telnet)

Não precisa de broker. Com o ESP "B" gravado e conectado ao Wi-Fi, de **outro computador na mesma rede**:

```bash
telnet <IP_DO_ESP_B> 23      # ou: nc <IP_DO_ESP_B> 23
```
No Windows, se `telnet` não existir: *Recursos do Windows → Cliente Telnet*. Deve aparecer, em texto puro:
```
login: admin
password: admin123
```
É exatamente isso que o HomeGuard detecta como risco (`docs/06-SEGURANCA.md`). As credenciais são **fictícias**.

## 7. Testes automáticos (sem hardware)

A lógica que não depende da placa (formatação da temperatura, reconexão, banner Telnet, validação do IP do broker) tem **22 testes unitários** que rodam no PC:

```bash
cd firmware
pio test -e native -v
```

O GitHub Actions (`.github/workflows/firmware-ci.yml`) roda esses testes e compila os dois firmwares em todo Pull Request que altera `firmware/`. **Um PR só deve ser aprovado com o CI verde.**

Se mudar uma constante do contrato (tópico MQTT, porta, intervalo) em `lib/homeguard_core/include/homeguard_core.h`, o teste `test_mqtt_contract_constants` falha de propósito: atualize o teste junto e combine a mudança com quem faz o backend.

## 8. Problemas comuns

| Sintoma | Causa provável e solução |
|---|---|
| `Falta include/secrets.h` | Você ainda não criou o `secrets.h` (seção 2.3). |
| `homeguard_core.h` / `homeguard_core.c: No such file or directory`, com os arquivos presentes | Caminho com acento/espaço ou dentro do OneDrive. Mova para `C:\homeguard\firmware` e apague a pasta `.pio` (seção 2.1). |
| `homeguard_core.h` não encontrado, e `firmware/lib/` não existe | Copiou só `esp_normal` ou `esp_vulneravel`. A pasta `firmware/` precisa estar inteira (o `platformio.ini` usa `lib_extra_dirs = ../lib`). |
| `Arduino.h`, `WiFi.h` ou `PubSubClient.h` sublinhados em vermelho | É o IntelliSense. Abra a pasta do projeto (não a raiz), rode o **Build** até terminar, depois `Ctrl+Shift+P → PlatformIO: Rebuild IntelliSense Index` e `Developer: Reload Window`. |
| Porta serial não aparece | Cabo só de carga, driver não instalado ou (Linux) usuário fora do grupo `dialout`. |
| `Wrong boot mode` / `Connecting......` infinito | Segure o botão **BOOT** durante o `Connecting...` (seção 3). |
| `[wifi] (re)conectando...` repetindo | SSID/senha errados, ou rede de 5 GHz. O ESP32 usa 2,4 GHz. |
| `[mqtt] falhou, rc=-2` | Não alcançou o broker. Veja a lista abaixo. |
| `[mqtt] falhou, rc=5` | Broker recusou (não autorizado): falta `allow_anonymous true` no `mosquitto.conf`. |
| `[config] HG_MQTT_BROKER_IP invalido em secrets.h` | O IP não é IPv4 válido (ex.: `192.168.0.25`, sem espaços e sem zeros à esquerda). Nome de host (`broker.exemplo.com`) **não** é aceito. |
| A placa reinicia sozinha ou trava ao conectar | Fonte USB fraca ou cabo ruim. Troque o cabo/porta. |

**`rc=-2` — checklist, nesta ordem:**

1. `netstat -an | findstr 1883` mostra `0.0.0.0:1883`? Se mostra `127.0.0.1`, o broker está só local (seção 4.2, itens b–e).
2. O serviço padrão do Mosquitto está ocupando a porta? `Stop-Service mosquitto` e inicie com `-c`.
3. O `HG_MQTT_BROKER_IP` é o IP do computador do broker, no adaptador certo, e **regravou** o ESP depois de mudar o `secrets.h`?
4. ESP e broker estão na mesma rede (mesmos três primeiros números do IP)?
5. `Test-NetConnection <IP_DO_BROKER> -Port 1883` dá `TcpTestSucceeded : True`? Se não, é firewall (perfil Público vs Privado, seção 4.2.g).
6. Redes de faculdade/visitantes e alguns roteadores **isolam os dispositivos entre si**. Teste com o hotspot de um celular ou um roteador próprio, que também é o que o projeto pede (rede de testes isolada).

## Usando Arduino IDE?

Estes projetos são para **PlatformIO**: a lógica compartilhada fica em `firmware/lib/`, fora de cada projeto, e a Arduino IDE não a enxerga. Se a equipe precisar da Arduino IDE, é possível gerar uma versão de sketch único (`.ino`).
