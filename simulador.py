"""
Simulador de sensores IoT -> QuestDB (ILP sobre HTTP).

Cada segundo genera una lectura por sensor (temperatura, humedad, vibracion).
De forma ocasional inyecta una anomalia (pico de temperatura) para que el
dashboard de Grafana muestre alertas.
"""
import math
import os
import random
import time

import requests
from questdb.ingress import Sender, TimestampNanos

HOST = os.getenv("QDB_HOST", "localhost")
PORT = int(os.getenv("QDB_HTTP_PORT", "9000"))
INTERVALO = float(os.getenv("INTERVALO_SEG", "1"))

SENSORES = [
    ("S01", "Sala_servidores"),
    ("S02", "Sala_servidores"),
    ("S03", "Bodega"),
    ("S04", "Bodega"),
    ("S05", "Produccion"),
]

DDL = """
CREATE TABLE IF NOT EXISTS sensores (
    ts TIMESTAMP,
    sensor_id SYMBOL,
    ubicacion SYMBOL,
    temperatura DOUBLE,
    humedad DOUBLE,
    vibracion DOUBLE
) TIMESTAMP(ts) PARTITION BY DAY WAL;
"""


def crear_tabla():
    """Crea la tabla via REST /exec; reintenta hasta que QuestDB responda."""
    for _ in range(30):
        try:
            r = requests.get(f"http://{HOST}:{PORT}/exec", params={"query": DDL}, timeout=5)
            r.raise_for_status()
            print("Tabla 'sensores' lista.")
            return
        except requests.RequestException as e:
            print(f"Esperando a QuestDB... ({e})")
            time.sleep(2)
    raise SystemExit("No se pudo conectar con QuestDB.")


def lectura(base_temp, t):
    temp = base_temp + 2.0 * math.sin(t / 60) + random.gauss(0, 0.3)
    hum = 55 + 8 * math.cos(t / 90) + random.gauss(0, 1.0)
    vib = abs(random.gauss(0.5, 0.15))
    # ~2 % de probabilidad de anomalia (pico de temperatura)
    if random.random() < 0.02:
        temp += random.uniform(8, 14)
        vib += random.uniform(1.0, 2.0)
    return round(temp, 2), round(hum, 2), round(vib, 3)


def main():
    crear_tabla()
    bases = {sid: random.uniform(22, 27) for sid, _ in SENSORES}
    inicio = time.time()
    conf = f"http::addr={HOST}:{PORT};"
    with Sender.from_conf(conf) as sender:
        while True:
            t = time.time() - inicio
            for sid, ubic in SENSORES:
                temp, hum, vib = lectura(bases[sid], t)
                sender.row(
                    "sensores",
                    symbols={"sensor_id": sid, "ubicacion": ubic},
                    columns={"temperatura": temp, "humedad": hum, "vibracion": vib},
                    at=TimestampNanos.now(),
                )
            sender.flush()
            print(f"[{time.strftime('%H:%M:%S')}] {len(SENSORES)} lecturas enviadas")
            time.sleep(INTERVALO)


if __name__ == "__main__":
    main()
