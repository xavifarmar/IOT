import asyncio
import websockets
import pandas as pd
from connection import connect_to_influxdb
import warnings
from influxdb_client.client.warnings import MissingPivotFunction

# Deshabilitar advertencias de PivotFunction de InfluxDB
warnings.simplefilter("ignore", MissingPivotFunction)

# Función para enviar datos de temperatura y humedad en tiempo real
async def send_temperature_data(websocket, client):
    """Envía datos de temperatura y humedad en tiempo real a los clientes conectados."""

    print("Cliente conectado.")
    await websocket.send("Bienvenido al servidor de datos IoT. Recibiendo datos de temperatura y humedad.")

    query_api = client.query_api()
    last_timestamp = None

    try:
        while True:
            # Consulta los últimos datos de temperatura
            query_temp = f'''
            from(bucket: "farm_iot")
                |> range(start: -10s)
                |> filter(fn: (r) => r["_measurement"] == "temperature_sensor")
                |> filter(fn: (r) => r["_field"] == "value")
            '''
            tables_temp = query_api.query_data_frame(query_temp)
           # print("Datos de temperatura crudos:", tables_temp)  # Depuración

            if tables_temp.empty:
                print("No hay datos de temperatura en el rango de tiempo especificado.")
            else:
                print("Datos de temperatura encontrados.")

                if '_start' in tables_temp.columns and '_value' in tables_temp.columns:
                    # Crear un nuevo DataFrame para evitar problemas de copia
                    df_temp = tables_temp[['_start', '_value']].copy()
                    df_temp.loc[:, '_start'] = pd.to_datetime(df_temp['_start'])
                    df_temp.rename(columns={'_start': 'Time', '_value': 'temperature'}, inplace=True)

                    if last_timestamp is None:
                        new_data_temp = df_temp
                    else:
                        new_data_temp = df_temp[df_temp['Time'] > last_timestamp]

                    if new_data_temp.empty:
                        print("No hay datos nuevos de temperatura para enviar.")
                    else:
                        # print(f"Datos nuevos de temperatura encontrados: {len(new_data_temp)} registros.")
                        last_timestamp = new_data_temp['Time'].max()
                        for _, row in new_data_temp.iterrows():
                            print(f"Enviando datos de temperatura: Tiempo: {row['Time']}, Temperatura: {row['temperature']}°C")
                            await websocket.send(f"Tiempo: {row['Time']}, Temperatura: {row['temperature']}°C")
                else:
                    print("Columnas '_start' y '_value' no encontradas en los datos de temperatura.")
                    print("Columnas disponibles:", tables_temp.columns)

            # Consulta los últimos datos de humedad
            query_hum = f'''
            from(bucket: "farm_iot")
                |> range(start: -10s)
                |> filter(fn: (r) => r["_measurement"] == "humidity_sensor")
                |> filter(fn: (r) => r["_field"] == "value")
            '''
            tables_hum = query_api.query_data_frame(query_hum)
           # print("Datos de humedad crudos:", tables_hum)  # Depuración

            if tables_hum.empty:
              print("No hay datos de humedad en el rango de tiempo especificado.")
            else:
                #print("Datos de humedad encontrados.")

                if '_start' in tables_hum.columns and '_value' in tables_hum.columns:
                    # print("Columnas '_start' y '_value' encontradas en los datos de humedad.")
                    # Crear un nuevo DataFrame para evitar problemas de copia
                    df_hum = tables_hum[['_start', '_value']].copy()
                    df_hum.loc[:, '_start'] = pd.to_datetime(df_hum['_start'])
                    df_hum.rename(columns={'_start': 'Time', '_value': 'humidity'}, inplace=True)

                    if last_timestamp is None:
                       # print("Primera consulta, enviando todos los datos de humedad.")
                        new_data_hum = df_hum
                    else:
                       # print(f"Filtrando datos de humedad con timestamp mayor a: {last_timestamp}")
                        new_data_hum = df_hum[df_hum['Time'] > last_timestamp]

                    if new_data_hum.empty:
                        print("No hay datos nuevos de humedad para enviar.")
                    else:
                      #  print(f"Datos nuevos de humedad encontrados: {len(new_data_hum)} registros.")
                        last_timestamp = new_data_hum['Time'].max()
                        for _, row in new_data_hum.iterrows():
                            print(f"Enviando datos de humedad: Tiempo: {row['Time']}, Humedad: {row['humidity']}%")
                            await websocket.send(f"Tiempo: {row['Time']}, Humedad: {row['humidity']}%")
                else:
                    print("Columnas '_start' y '_value' no encontradas en los datos de humedad.")
                    print("Columnas disponibles:", tables_hum.columns)

            await asyncio.sleep(5)  # Pausa entre consultas
    except websockets.exceptions.ConnectionClosed:
        print("Conexión cerrada con el cliente.")
    except Exception as e:
        print(f"Error inesperado: {e}")

# Configurar el servidor WebSocket
async def main():
    # Conectar correctamente a InfluxDB
    client = connect_to_influxdb()  # Esto ahora devuelve un objeto InfluxDBClient
    server = await websockets.serve(lambda ws, path: send_temperature_data(ws, client), "0.0.0.0", 8765)
    print("Servidor WebSocket iniciado en ws://0.0.0.0:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())