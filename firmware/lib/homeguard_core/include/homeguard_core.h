// HomeGuard — lógica portável do firmware.
//
// Este módulo NÃO depende de Arduino/ESP32: ele compila tanto no ESP quanto no
// PC (env `native` do PlatformIO). É isso que permite testá-lo no GitHub Actions
// sem hardware. Qualquer regra que possa ser testada sem placa deve morar aqui;
// os main.cpp ficam só com a "cola" de Wi-Fi/MQTT/Telnet.
#ifndef HOMEGUARD_CORE_H
#define HOMEGUARD_CORE_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// ---- Constantes de protocolo (contrato com o backend / docs/02) -------------

#define HG_MQTT_PORT 1883
#define HG_TELNET_PORT 23
#define HG_MQTT_TOPIC_TEMPERATURE "homeguard/sensores/temperatura"
#define HG_MQTT_CLIENT_ID "esp32-sensor-temperatura"

// Intervalo entre publicações do sensor normal (ms).
#define HG_PUBLISH_INTERVAL_MS 5000u

// Limites da simulação de temperatura (décimos de grau em torno de 20.0 °C).
#define HG_TEMP_BASE_C 20.0f
#define HG_TEMP_JITTER_MIN_TENTHS (-20)  // inclusivo
#define HG_TEMP_JITTER_MAX_TENTHS 20     // exclusivo (igual ao random() do Arduino)

// Backoff de reconexão (ms).
#define HG_BACKOFF_BASE_MS 500u
#define HG_BACKOFF_MAX_MS 30000u

// ---- Sensor de temperatura simulado ----------------------------------------

// Converte um valor inteiro vindo de random(MIN, MAX) em temperatura (°C).
// Valores fora do intervalo são "presos" (clamp) aos limites.
float hg_temperature_from_jitter(int jitter_tenths);

// Escreve a temperatura como texto com 2 casas decimais (ex.: "21.30").
// Retorna o número de caracteres escritos (sem o '\0'), ou -1 se buf for
// inválido ou pequeno demais. buf_size recomendado: >= 16.
int hg_format_temperature(float celsius, char *buf, size_t buf_size);

// ---- Reconexão -------------------------------------------------------------

// Espera (ms) antes da tentativa número `attempt` (0, 1, 2, ...):
// 500, 1000, 2000, ... limitado a HG_BACKOFF_MAX_MS. Nunca estoura.
uint32_t hg_backoff_ms(uint32_t attempt);

// Decide se já passou o intervalo desde a última ação, tolerando o estouro do
// contador millis() (que volta a zero a cada ~49 dias).
int hg_interval_elapsed(uint32_t now_ms, uint32_t last_ms, uint32_t interval_ms);

// ---- Telnet vulnerável (SOMENTE rede de testes isolada — docs/06) ----------

// Credenciais FICTÍCIAS usadas de propósito no ESP "B". Nunca reutilize
// credenciais reais aqui (checklist de docs/06-SEGURANCA.md).
#define HG_FAKE_TELNET_USER "admin"
#define HG_FAKE_TELNET_PASS "admin123"

// Monta o banner que o ESP vulnerável envia em texto puro ao conectar.
// Retorna o número de caracteres escritos ou -1 se o buffer for pequeno demais.
int hg_build_telnet_banner(char *buf, size_t buf_size);

// ---- Validação de configuração ---------------------------------------------

// 1 se `s` é um IPv4 decimal válido ("192.168.4.10"), 0 caso contrário.
// Usado para falhar cedo se o IP do broker em secrets.h estiver errado.
int hg_is_valid_ipv4(const char *s);

#ifdef __cplusplus
}
#endif

#endif  // HOMEGUARD_CORE_H
