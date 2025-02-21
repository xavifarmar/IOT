import random
import time
from datetime import datetime
#from influxdb_client import InfluxDBClient, Point, WritePrecision
from connection import connect_to_influxdb, write_to_influxdb

# Obtener cliente y API de escritura de InfluxDB
client = connect_to_influxdb()

#Crear temperatura del termometro
def temperature_sensor(client):
    
    thermometer_data = float(24)
    """Simula los datos que proporciona un termometro en grados Celsius cada segundo
        y los envia a influxDB """
    
    while True:

        thermometer_data += float(random.uniform(-0.8, 0.8))
        
        timestamp = int(time.time() * 1000) #Tiempo en milisegundos
        timeactual = time.time()
        current_time = datetime.fromtimestamp(timeactual).strftime("%H:%M:%S")
        
        # Enviar el punto de datos a InfluxDB
        try:   
            write_to_influxdb(client, "temperature_sensor", thermometer_data, timestamp)
        except Exception as e:
            print(f"No ha sido posible enviar los datos a influxDB {e}")

        print(f"Temperatura: {thermometer_data}Cº | {current_time}")
        time.sleep(5)
        
