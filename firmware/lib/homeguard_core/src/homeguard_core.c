#include "homeguard_core.h"

#include <stdio.h>
#include <string.h>

float hg_temperature_from_jitter(int jitter_tenths) {
  if (jitter_tenths < HG_TEMP_JITTER_MIN_TENTHS) {
    jitter_tenths = HG_TEMP_JITTER_MIN_TENTHS;
  }
  // MAX é exclusivo no random() do Arduino, mas aceitamos o limite superior
  // como valor válido para não rejeitar entrada de teste.
  if (jitter_tenths > HG_TEMP_JITTER_MAX_TENTHS) {
    jitter_tenths = HG_TEMP_JITTER_MAX_TENTHS;
  }
  return HG_TEMP_BASE_C + (float)jitter_tenths / 10.0f;
}

int hg_format_temperature(float celsius, char *buf, size_t buf_size) {
  if (buf == NULL || buf_size == 0) {
    return -1;
  }
  int n = snprintf(buf, buf_size, "%.2f", (double)celsius);
  if (n < 0 || (size_t)n >= buf_size) {
    buf[0] = '\0';
    return -1;
  }
  return n;
}

uint32_t hg_backoff_ms(uint32_t attempt) {
  // 500 << 6 = 32000 > MAX; limitar o deslocamento evita overflow em uint32_t.
  if (attempt >= 7) {
    return HG_BACKOFF_MAX_MS;
  }
  uint32_t delay = HG_BACKOFF_BASE_MS << attempt;
  return delay > HG_BACKOFF_MAX_MS ? HG_BACKOFF_MAX_MS : delay;
}

int hg_interval_elapsed(uint32_t now_ms, uint32_t last_ms, uint32_t interval_ms) {
  // Subtração sem sinal é correta mesmo após o millis() dar a volta.
  return (uint32_t)(now_ms - last_ms) >= interval_ms;
}

int hg_build_telnet_banner(char *buf, size_t buf_size) {
  if (buf == NULL || buf_size == 0) {
    return -1;
  }
  int n = snprintf(buf, buf_size, "login: %s\r\npassword: %s\r\n",
                   HG_FAKE_TELNET_USER, HG_FAKE_TELNET_PASS);
  if (n < 0 || (size_t)n >= buf_size) {
    buf[0] = '\0';
    return -1;
  }
  return n;
}

int hg_is_valid_ipv4(const char *s) {
  if (s == NULL || *s == '\0') {
    return 0;
  }
  int octets = 0;
  const char *p = s;
  while (*p != '\0') {
    if (*p < '0' || *p > '9') {
      return 0;
    }
    int digits = 0;
    int value = 0;
    const char *start = p;
    while (*p >= '0' && *p <= '9') {
      value = value * 10 + (*p - '0');
      digits++;
      p++;
      if (digits > 3) {
        return 0;
      }
    }
    if (value > 255) {
      return 0;
    }
    if (digits > 1 && *start == '0') {  // sem zeros à esquerda ("01")
      return 0;
    }
    octets++;
    if (*p == '.') {
      p++;
      if (*p == '\0') {  // termina em ponto
        return 0;
      }
    } else if (*p != '\0') {
      return 0;
    }
  }
  return octets == 4;
}
