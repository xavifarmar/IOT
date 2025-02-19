from influxdb_client.rest import ApiException
from connection_component import InfluxDBConnection

def read_last_temperature():
    """Lee el último valor de temperatura desde InfluxDB."""
    connection = InfluxDBConnection(
        url="http://192.168.105.110:8086",
        token="ejmO_FbDgQVx_OMFFLxO8cEjYpPzZx_QdMEy0VHpSSr3DC7idArwcj1CSvhqyBG_alzh72D8Xd7sGDEtjkBjsg==",
        org="jmh",
        bucket="jmh"
    )
    
    client = connection.get_client()
    query_api = connection.get_query_api(client)
    
    query = f'''
    from(bucket: "{connection.bucket}")
        |> range(start: -10m)
        |> filter(fn: (r) => r._measurement == "thermometer" and r._field == "temperature")
        |> last()
    '''

    try:
        tables = query_api.query(query)
        for table in tables:
            for record in table.records:
                print(f"Última temperatura registrada: {record.get_value()}°C")
    except ApiException as e:
        print(f"Error al consultar InfluxDB: {e}")

if __name__ == "__main__":
    read_last_temperature()
