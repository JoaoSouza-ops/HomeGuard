FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir paho-mqtt==2.1.0
COPY sim_esp.py check.py ./
# Roda como root só para poder abrir a porta 23 (privilegiada) — container exclusivo de teste local.
CMD ["python", "-u", "sim_esp.py"]
