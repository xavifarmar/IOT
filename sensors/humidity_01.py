import random
import time
from datetime import datetime
#from influxdb_client import InfluxDBClient, Point, WritePrecision
from connection import connect_to_influxdb, write_to_influxdb

# Obtener cliente y API de escritura de InfluxDB
client = connect_to_influxdb()

# Función para simular la lectura de humedad
def humidity_sensor(client):
    
    while True:
        humidity = random.randint(40, 70)  # Humedad entre 40% y 70%

        timestamp = int(time.time() * 1000)  #Tiempo en milisegundos
        timeactual = time.time()
        current_time = datetime.fromtimestamp(timeactual).strftime("%H:%M:%S")
        
        # Enviar el punto de datos a InfluxD
        try:   
           write_to_influxdb(client, "humidity_sensor", humidity, timestamp)
        except Exception as e:
            print(f"No ha sido posible enviar los datos a influxDB {e}")
    
        
        print(f"Humedad: {humidity} % | {current_time}")
        
        time.sleep(5)
