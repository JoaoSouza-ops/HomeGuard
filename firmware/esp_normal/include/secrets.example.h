// Copie para `secrets.h` (ignorado pelo Git) e preencha com os dados da
// REDE DE TESTES. Nunca commite o secrets.h real.
//   cp secrets.example.h secrets.h
#ifndef HG_SECRETS_H
#define HG_SECRETS_H

#define HG_WIFI_SSID "NOME_DA_REDE_DE_TESTES"
#define HG_WIFI_PASSWORD "SENHA_DA_REDE"

// IP do broker Mosquitto (docs/07). Ajuste para a faixa da rede de testes.
#define HG_MQTT_BROKER_IP "192.168.4.10"

#endif  // HG_SECRETS_H
