// ESP "A" — dispositivo normal: sensor de temperatura simulado publicando via MQTT.
// A lógica testável fica em lib/homeguard_core; aqui só a "cola" com Wi-Fi/MQTT.
#include <Arduino.h>
#include <PubSubClient.h>
#include <WiFi.h>

#include "homeguard_core.h"

// secrets.h não vai para o Git: crie-o a partir de include/secrets.example.h
// (passo a passo em firmware/README.md).
#if __has_include("secrets.h")
#include "secrets.h"
#else
#error "Falta include/secrets.h. Copie include/secrets.example.h para include/secrets.h e preencha (veja firmware/README.md)."
#endif

static WiFiClient wifiClient;
static PubSubClient mqtt(wifiClient);

static uint32_t lastPublishMs = 0;
static uint32_t lastWifiTryMs = 0;
static uint32_t lastMqttTryMs = 0;
static uint32_t wifiAttempt = 0;
static uint32_t mqttAttempt = 0;
static bool configOk = true;

// Conecta ao Wi-Fi sem travar o loop: retorna true se já está conectado.
static bool ensureWifi(uint32_t now) {
  if (WiFi.status() == WL_CONNECTED) {
    if (wifiAttempt != 0) {
      Serial.print("[wifi] conectado, IP ");
      Serial.println(WiFi.localIP());
    }
    wifiAttempt = 0;
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

static bool ensureMqtt(uint32_t now) {
  if (mqtt.connected()) {
    mqttAttempt = 0;
    return true;
  }
  if (hg_interval_elapsed(now, lastMqttTryMs, hg_backoff_ms(mqttAttempt))) {
    Serial.println("[mqtt] conectando ao broker...");
    lastMqttTryMs = now;
    if (mqtt.connect(HG_MQTT_CLIENT_ID)) {
      Serial.println("[mqtt] conectado");
      mqttAttempt = 0;
      return true;
    }
    Serial.print("[mqtt] falhou, rc=");
    Serial.println(mqtt.state());
    mqttAttempt++;
  }
  return false;
}

static void publishTemperature() {
  int jitter = (int)random(HG_TEMP_JITTER_MIN_TENTHS, HG_TEMP_JITTER_MAX_TENTHS);
  float celsius = hg_temperature_from_jitter(jitter);

  char payload[16];
  if (hg_format_temperature(celsius, payload, sizeof(payload)) < 0) {
    Serial.println("[sensor] erro ao formatar temperatura");
    return;
  }
  if (mqtt.publish(HG_MQTT_TOPIC_TEMPERATURE, payload)) {
    Serial.print("[sensor] publicado: ");
    Serial.println(payload);
  } else {
    Serial.println("[sensor] falha ao publicar");
  }
}

void setup() {
  Serial.begin(115200);
  randomSeed(esp_random());

  if (!hg_is_valid_ipv4(HG_MQTT_BROKER_IP)) {
    Serial.println("[config] HG_MQTT_BROKER_IP invalido em secrets.h");
    configOk = false;
    return;
  }
  mqtt.setServer(HG_MQTT_BROKER_IP, HG_MQTT_PORT);
  WiFi.mode(WIFI_STA);
  WiFi.begin(HG_WIFI_SSID, HG_WIFI_PASSWORD);
}

void loop() {
  if (!configOk) {
    delay(1000);
    return;
  }
  uint32_t now = millis();

  if (!ensureWifi(now) || !ensureMqtt(now)) {
    return;
  }
  mqtt.loop();

  if (hg_interval_elapsed(now, lastPublishMs, HG_PUBLISH_INTERVAL_MS)) {
    lastPublishMs = now;
    publishTemperature();
  }
}
