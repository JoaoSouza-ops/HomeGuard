"""Simulador dos 2 ESPs do HomeGuard (para testar SEM o hardware).

Imita exatamente o firmware (firmware/lib/homeguard_core):
  - ESP "A": publica a temperatura (ex.: "21.30") a cada 5 s no tópico MQTT
    homeguard/sensores/temperatura, com client id esp32-sensor-temperatura.
  - ESP "B": porta 23 (Telnet) que envia login/senha FICTÍCIOS em texto puro.
USO SOMENTE LOCAL / REDE DE TESTES. Não sobe na AWS.
"""
import asyncio
import os
import random

import paho.mqtt.client as mqtt

MQTT_HOST = os.getenv("MQTT_HOST", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
INTERVALO = float(os.getenv("PUBLISH_INTERVAL", "5"))
TELNET_PORT = int(os.getenv("TELNET_PORT", "23"))

TOPICO = "homeguard/sensores/temperatura"
CLIENT_ID = "esp32-sensor-temperatura"
BANNER = b"login: admin\r\npassword: admin123\r\n"


def gerar_temperatura() -> str:
    # igual ao firmware: 20.0 + random(-20, 20)/10, com 2 casas decimais
    return f"{20.0 + random.randrange(-20, 20) / 10.0:.2f}"


async def publicar(cliente: mqtt.Client) -> None:
    while True:
        payload = gerar_temperatura()
        info = cliente.publish(TOPICO, payload)
        estado = "ok" if info.rc == mqtt.MQTT_ERR_SUCCESS else f"falhou (rc={info.rc})"
        print(f"[sim-esp-a] {TOPICO} = {payload} -> {estado}", flush=True)
        await asyncio.sleep(INTERVALO)


async def atender_telnet(reader, writer) -> None:
    origem = writer.get_extra_info("peername")
    print(f"[sim-esp-b] conexao telnet de {origem}", flush=True)
    writer.write(BANNER)
    await writer.drain()
    writer.close()


async def main() -> None:
    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
    cliente.reconnect_delay_set(min_delay=1, max_delay=30)
    cliente.connect_async(MQTT_HOST, MQTT_PORT)
    cliente.loop_start()
    servidor = await asyncio.start_server(atender_telnet, "0.0.0.0", TELNET_PORT)
    print(f"[sim] MQTT -> {MQTT_HOST}:{MQTT_PORT} | Telnet na porta {TELNET_PORT}", flush=True)
    async with servidor:
        await asyncio.gather(publicar(cliente), servidor.serve_forever())


if __name__ == "__main__":
    asyncio.run(main())
