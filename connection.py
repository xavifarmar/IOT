import os
from influxdb_client import InfluxDBClient, Point, WritePrecision

class InfluxDBConnection:
    def __init__(self, url, token, org, bucket):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket

def get_client(self):
        """Devuelve una instancia del cliente de InfluxDB."""
        return InfluxDBClient(url=self.url, token=self.token, org=self.org)

def get_query_api(self, client):
    """Obtiene la API de consulta."""
    return client.query_api()

# Conectar a InfluxDB
def connect_to_influxdb():
    client = InfluxDBClient(
        url="http://localhost:8086", 
        token="Obzc66q1bvHbtsbH1claJPfnhcrGV51-P9cCf-1RNE5zcuR4z0XX1z-3N3_YI6kVIJwtS6bTmlCKUbMLGZIraA==", 
        org="xfm",
        bucket = "farm_iot"
    )
    return client


# Función para escribir datos en InfluxDB
def write_to_influxdb(client, sensor_name, sensor_value, timestamp):
    #Creacion de punto de datos
    point = Point(sensor_name) \
        .field("value", sensor_value) \
        .time(timestamp, WritePrecision.MS)
    
    #Escritura en la base de datos
    write_api = client.write_api()
    write_api.write(bucket="farm_iot", record=point)

