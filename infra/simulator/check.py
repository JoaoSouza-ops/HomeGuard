"""Verificação rápida de que a pilha local funciona (3 testes). Sai com código 1 se algo falhar.

  docker compose ... run --rm esp-sim python check.py
Variáveis opcionais: API_URL, MQTT_HOST, TELNET_HOST (use o IP do ESP B real para testar a placa).
"""
import os
import socket
import sys
import threading
import urllib.error
import urllib.request

import paho.mqtt.client as mqtt

API_URL = os.getenv("API_URL", "http://caddy/api")
MQTT_HOST = os.getenv("MQTT_HOST", "mosquitto")
TELNET_HOST = os.getenv("TELNET_HOST", "esp-sim")
TOPICO = "homeguard/sensores/temperatura"
falhas = 0


def resultado(ok: bool, texto: str) -> None:
    global falhas
    falhas += 0 if ok else 1
    print(("[ OK ] " if ok else "[FALHA] ") + texto, flush=True)


def testar_api() -> None:
    try:
        with urllib.request.urlopen(API_URL + "/openapi.json", timeout=5) as r:
            resultado(r.status == 200, f"API responde em {API_URL}/openapi.json")
    except Exception as e:  # noqa: BLE001
        resultado(False, f"API nao responde ({e})")
        return
    try:
        with urllib.request.urlopen(API_URL + "/health", timeout=5) as r:
            print(f"       /health -> {r.status} {r.read().decode()}")
    except urllib.error.HTTPError as e:
        print(f"       /health -> {e.code} (rota ainda nao existe: aguarda a PR das rotas)")


def testar_mqtt() -> None:
    chegou = threading.Event()
    msg = {}

    def ao_receber(_c, _u, m):
        msg["v"] = m.payload.decode()
        chegou.set()

    try:
        c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="hg-check")
        c.on_message = ao_receber
        c.on_connect = lambda cl, *_a: cl.subscribe(TOPICO)
        c.connect(MQTT_HOST, 1883, 10)
        c.loop_start()
        ok = chegou.wait(15)
        c.loop_stop()
        resultado(ok, f"broker MQTT recebeu {TOPICO} = {msg.get('v', '-')}"
                  if ok else "nenhuma mensagem MQTT em 15 s (ESP/simulador ligado?)")
    except Exception as e:  # noqa: BLE001
        resultado(False, f"broker MQTT inacessivel ({e})")


def testar_telnet() -> None:
    try:
        with socket.create_connection((TELNET_HOST, 23), timeout=5) as s:
            dado = s.recv(128).decode(errors="replace")
        resultado("login:" in dado, f"Telnet {TELNET_HOST}:23 devolveu o banner inseguro")
    except Exception as e:  # noqa: BLE001
        resultado(False, f"Telnet {TELNET_HOST}:23 inacessivel ({e})")


if __name__ == "__main__":
    testar_api()
    testar_mqtt()
    testar_telnet()
    print("\nTudo certo!" if falhas == 0 else f"\n{falhas} teste(s) com falha.")
    sys.exit(1 if falhas else 0)
