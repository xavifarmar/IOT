import random
import time
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS
from connection_component import InfluxDBConnection

def simulate_temperature_data():
    """Simula el envío de datos de temperatura cada 5 segundos."""
    connection = InfluxDBConnection(
        url="http://10.0.2.15:8086",
        token="Obzc66q1bvHbtsbH1claJPfnhcrGV51-P9cCf-1RNE5zcuR4z0XX1z-3N3_YI6kVIJwtS6bTmlCKUbMLGZIraA==",
        org="xfm",
        bucket="xfm"
    )
    
    client = connection.get_client()
    write_api = connection.get_write_api(client)

    try:
        while True:
            # Genera datos de temperatura aleatoria entre 20 y 30 grados.
            temperature = round(random.uniform(20, 30), 2)
            point = Point("thermometer").field("temperature", temperature)
            write_api.write(bucket=connection.bucket, org=connection.org, record=point)
            print(f"Temperatura enviada: {temperature}°C")
            time.sleep(5)  # Simula el envío cada 5 segundos
    except KeyboardInterrupt:
        print("Simulación detenida.")

if __name__ == "__main__":
    simulate_temperature_data()
