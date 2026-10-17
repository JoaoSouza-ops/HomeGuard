// ESP "B" — dispositivo VULNERÁVEL DE PROPÓSITO.
//
// Abre a porta 23 (Telnet) e envia um usuário/senha FICTÍCIOS em texto puro a
// qualquer conexão (CWE-319 / T1040 — ver docs/06-SEGURANCA.md).
// Use SOMENTE na rede de testes isolada. Não reutilize credenciais reais.
#include <Arduino.h>
#include <WiFi.h>

#include "homeguard_core.h"

// secrets.h não vai para o Git: crie-o a partir de include/secrets.example.h
// (passo a passo em firmware/README.md).
#if __has_include("secrets.h")
#include "secrets.h"
#else
#error "Falta include/secrets.h. Copie include/secrets.example.h para include/secrets.h e preencha (veja firmware/README.md)."
#endif

static WiFiServer telnetServer(HG_TELNET_PORT);

static uint32_t lastWifiTryMs = 0;
static uint32_t wifiAttempt = 0;
static bool serverStarted = false;

static bool ensureWifi(uint32_t now) {
  if (WiFi.status() == WL_CONNECTED) {
    if (wifiAttempt != 0) {
      Serial.print("[wifi] conectado, IP ");
      Serial.println(WiFi.localIP());
    }
    wifiAttempt = 0;
    if (!serverStarted) {
      telnetServer.begin();
      serverStarted = true;
      Serial.println("[telnet] servidor vulneravel ouvindo na porta 23");
    }
    return true;
  }
  if (hg_interval_elapsed(now, lastWifiTryMs, hg_backoff_ms(wifiAttempt))) {
    Serial.println("[wifi] (re)conectando...");
    WiFi.disconnect();
    WiFi.begin(HG_WIFI_SSID, HG_WIFI_PASSWORD);
    lastWifiTryMs = now;
    wifiAttempt++;
  }
  return false;
}

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.begin(HG_WIFI_SSID, HG_WIFI_PASSWORD);
}

void loop() {
  if (!ensureWifi(millis())) {
    return;
  }

  WiFiClient client = telnetServer.available();
  if (client) {
    char banner[64];
    int n = hg_build_telnet_banner(banner, sizeof(banner));
    if (n > 0) {
      client.write((const uint8_t *)banner, (size_t)n);
    }
    Serial.print("[telnet] conexao de ");
    Serial.println(client.remoteIP());
    client.stop();
  }
}
