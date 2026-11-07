#include <string.h>
#include <unity.h>

#include "homeguard_core.h"

void setUp(void) {}
void tearDown(void) {}

// ---- Temperatura -----------------------------------------------------------

void test_temperature_zero_jitter_is_base(void) {
  TEST_ASSERT_FLOAT_WITHIN(0.001f, 20.0f, hg_temperature_from_jitter(0));
}

void test_temperature_positive_and_negative_jitter(void) {
  TEST_ASSERT_FLOAT_WITHIN(0.001f, 21.3f, hg_temperature_from_jitter(13));
  TEST_ASSERT_FLOAT_WITHIN(0.001f, 18.5f, hg_temperature_from_jitter(-15));
}

void test_temperature_is_clamped_to_limits(void) {
  TEST_ASSERT_FLOAT_WITHIN(0.001f, 18.0f, hg_temperature_from_jitter(-9999));
  TEST_ASSERT_FLOAT_WITHIN(0.001f, 22.0f, hg_temperature_from_jitter(9999));
}

void test_temperature_always_in_expected_range(void) {
  for (int j = HG_TEMP_JITTER_MIN_TENTHS; j < HG_TEMP_JITTER_MAX_TENTHS; j++) {
    float t = hg_temperature_from_jitter(j);
    TEST_ASSERT_TRUE(t >= 18.0f && t <= 22.0f);
  }
}

void test_format_temperature_two_decimals(void) {
  char buf[16];
  TEST_ASSERT_EQUAL_INT(5, hg_format_temperature(21.3f, buf, sizeof(buf)));
  TEST_ASSERT_EQUAL_STRING("21.30", buf);
}

void test_format_temperature_negative(void) {
  char buf[16];
  TEST_ASSERT_EQUAL_INT(5, hg_format_temperature(-3.5f, buf, sizeof(buf)));
  TEST_ASSERT_EQUAL_STRING("-3.50", buf);
}

void test_format_temperature_rejects_small_buffer(void) {
  char buf[4];
  TEST_ASSERT_EQUAL_INT(-1, hg_format_temperature(21.3f, buf, sizeof(buf)));
  TEST_ASSERT_EQUAL_STRING("", buf);
}

void test_format_temperature_rejects_null_and_zero_size(void) {
  char buf[16];
  TEST_ASSERT_EQUAL_INT(-1, hg_format_temperature(21.3f, NULL, 16));
  TEST_ASSERT_EQUAL_INT(-1, hg_format_temperature(21.3f, buf, 0));
}

void test_payload_fits_in_firmware_buffer(void) {
  // O firmware usa char payload[16]; o pior caso precisa caber.
  char buf[16];
  TEST_ASSERT_TRUE(hg_format_temperature(22.0f, buf, sizeof(buf)) > 0);
  TEST_ASSERT_TRUE(hg_format_temperature(18.0f, buf, sizeof(buf)) > 0);
}

// ---- Backoff e intervalo ---------------------------------------------------

void test_backoff_grows_exponentially(void) {
  TEST_ASSERT_EQUAL_UINT32(500, hg_backoff_ms(0));
  TEST_ASSERT_EQUAL_UINT32(1000, hg_backoff_ms(1));
  TEST_ASSERT_EQUAL_UINT32(2000, hg_backoff_ms(2));
  TEST_ASSERT_EQUAL_UINT32(4000, hg_backoff_ms(3));
}

void test_backoff_is_capped_and_never_overflows(void) {
  TEST_ASSERT_EQUAL_UINT32(HG_BACKOFF_MAX_MS, hg_backoff_ms(6));
  TEST_ASSERT_EQUAL_UINT32(HG_BACKOFF_MAX_MS, hg_backoff_ms(7));
  TEST_ASSERT_EQUAL_UINT32(HG_BACKOFF_MAX_MS, hg_backoff_ms(100));
  TEST_ASSERT_EQUAL_UINT32(HG_BACKOFF_MAX_MS, hg_backoff_ms(0xFFFFFFFFu));
}

void test_interval_not_elapsed_yet(void) {
  TEST_ASSERT_FALSE(hg_interval_elapsed(1000, 0, 5000));
  TEST_ASSERT_FALSE(hg_interval_elapsed(4999, 0, 5000));
}

void test_interval_elapsed_exactly_and_after(void) {
  TEST_ASSERT_TRUE(hg_interval_elapsed(5000, 0, 5000));
  TEST_ASSERT_TRUE(hg_interval_elapsed(9000, 0, 5000));
}

void test_interval_handles_millis_rollover(void) {
  // last perto do limite de uint32_t; now já deu a volta (~49 dias de uptime).
  uint32_t last = 0xFFFFFF00u;
  TEST_ASSERT_FALSE(hg_interval_elapsed(0x00000100u, last, 5000));  // passaram 512 ms
  TEST_ASSERT_TRUE(hg_interval_elapsed(0x00002000u, last, 5000));   // passaram ~8.4 s
}

// ---- Telnet vulnerável -----------------------------------------------------

void test_telnet_banner_contains_fake_credentials(void) {
  char buf[64];
  int n = hg_build_telnet_banner(buf, sizeof(buf));
  TEST_ASSERT_TRUE(n > 0);
  TEST_ASSERT_EQUAL_INT((int)strlen(buf), n);
  TEST_ASSERT_NOT_NULL(strstr(buf, "login: admin"));
  TEST_ASSERT_NOT_NULL(strstr(buf, "password: admin123"));
}

void test_telnet_banner_uses_crlf_line_endings(void) {
  char buf[64];
  hg_build_telnet_banner(buf, sizeof(buf));
  TEST_ASSERT_NOT_NULL(strstr(buf, "\r\n"));
}

void test_telnet_banner_fits_in_firmware_buffer(void) {
  // O firmware usa char banner[64].
  char buf[64];
  TEST_ASSERT_TRUE(hg_build_telnet_banner(buf, sizeof(buf)) > 0);
}

void test_telnet_banner_rejects_small_buffer(void) {
  char buf[8];
  TEST_ASSERT_EQUAL_INT(-1, hg_build_telnet_banner(buf, sizeof(buf)));
  TEST_ASSERT_EQUAL_INT(-1, hg_build_telnet_banner(NULL, 64));
}

void test_telnet_port_is_23(void) {
  TEST_ASSERT_EQUAL_INT(23, HG_TELNET_PORT);
}

// ---- Contrato com o backend (docs/02, docs/03) -----------------------------

void test_mqtt_contract_constants(void) {
  TEST_ASSERT_EQUAL_STRING("homeguard/sensores/temperatura", HG_MQTT_TOPIC_TEMPERATURE);
  TEST_ASSERT_EQUAL_INT(1883, HG_MQTT_PORT);
  TEST_ASSERT_EQUAL_STRING("esp32-sensor-temperatura", HG_MQTT_CLIENT_ID);
  TEST_ASSERT_EQUAL_UINT32(5000, HG_PUBLISH_INTERVAL_MS);
}

// ---- Validação de IPv4 -----------------------------------------------------

void test_ipv4_valid_addresses(void) {
  TEST_ASSERT_TRUE(hg_is_valid_ipv4("192.168.4.10"));
  TEST_ASSERT_TRUE(hg_is_valid_ipv4("0.0.0.0"));
  TEST_ASSERT_TRUE(hg_is_valid_ipv4("255.255.255.255"));
  TEST_ASSERT_TRUE(hg_is_valid_ipv4("10.0.0.1"));
}

void test_ipv4_invalid_addresses(void) {
  TEST_ASSERT_FALSE(hg_is_valid_ipv4(NULL));
  TEST_ASSERT_FALSE(hg_is_valid_ipv4(""));
  TEST_ASSERT_FALSE(hg_is_valid_ipv4("192.168.4"));
  TEST_ASSERT_FALSE(hg_is_valid_ipv4("192.168.4.10.5"));
  TEST_ASSERT_FALSE(hg_is_valid_ipv4("256.1.1.1"));
  TEST_ASSERT_FALSE(hg_is_valid_ipv4("192.168.4."));
  TEST_ASSERT_FALSE(hg_is_valid_ipv4(".192.168.4.1"));
  TEST_ASSERT_FALSE(hg_is_valid_ipv4("192..168.4"));
  TEST_ASSERT_FALSE(hg_is_valid_ipv4("192.168.4.a"));
  TEST_ASSERT_FALSE(hg_is_valid_ipv4("192.168.04.1"));
  TEST_ASSERT_FALSE(hg_is_valid_ipv4("1234.1.1.1"));
  TEST_ASSERT_FALSE(hg_is_valid_ipv4("192.168.4.10 "));
}

int main(void) {
  UNITY_BEGIN();

  RUN_TEST(test_temperature_zero_jitter_is_base);
  RUN_TEST(test_temperature_positive_and_negative_jitter);
  RUN_TEST(test_temperature_is_clamped_to_limits);
  RUN_TEST(test_temperature_always_in_expected_range);
  RUN_TEST(test_format_temperature_two_decimals);
  RUN_TEST(test_format_temperature_negative);
  RUN_TEST(test_format_temperature_rejects_small_buffer);
  RUN_TEST(test_format_temperature_rejects_null_and_zero_size);
  RUN_TEST(test_payload_fits_in_firmware_buffer);

  RUN_TEST(test_backoff_grows_exponentially);
  RUN_TEST(test_backoff_is_capped_and_never_overflows);
  RUN_TEST(test_interval_not_elapsed_yet);
  RUN_TEST(test_interval_elapsed_exactly_and_after);
  RUN_TEST(test_interval_handles_millis_rollover);

  RUN_TEST(test_telnet_banner_contains_fake_credentials);
  RUN_TEST(test_telnet_banner_uses_crlf_line_endings);
  RUN_TEST(test_telnet_banner_fits_in_firmware_buffer);
  RUN_TEST(test_telnet_banner_rejects_small_buffer);
  RUN_TEST(test_telnet_port_is_23);

  RUN_TEST(test_mqtt_contract_constants);

  RUN_TEST(test_ipv4_valid_addresses);
  RUN_TEST(test_ipv4_invalid_addresses);

  return UNITY_END();
}
