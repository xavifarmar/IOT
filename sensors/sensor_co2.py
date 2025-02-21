import random
import time
from datetime import datetime
#from influxdb_client import InfluxDBClient, Point, WritePrecision
from connection import connect_to_influxdb, write_to_influxdb

# Obtener cliente y API de escritura de InfluxDB
client = connect_to_influxdb()

# Simulación de datos del sensor de CO2
def co2_sensor(client):
    
    co2_data = float(400)  # Valor inicial de CO2 (en ppm)
    """Simula los datos que proporciona un sensor de CO2 (en ppm) cada segundo
        y los envia a InfluxDB """
    
    while True:
        # Simula los valores de CO2 fluctuando entre +/- 20 ppm
        co2_data += random.uniform(-20, 20)
        
        # Limita el valor para que no sea negativo ni excesivamente alto
        co2_data = max(0, min(co2_data, 5000))  # Rango típico de CO2: 0-5000 ppm
        
        timestamp = int(time.time() * 1000)  # Tiempo en milisegundos
        timeactual = time.time()
        current_time = datetime.fromtimestamp(timeactual).strftime("%H:%M:%S")
        
        # Enviar el punto de datos a InfluxDB
        try:
            write_to_influxdb(client, "co2_sensor", co2_data, timestamp)
        except Exception as e:
            print(f"No ha sido posible enviar los datos a InfluxDB: {e}")

        print(f"CO2: {co2_data} ppm | {current_time}")
        time.sleep(5)

# Ejecutar simulación de sensores
co2_sensor(client)
