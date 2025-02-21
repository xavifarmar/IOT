import asyncio
import websockets
import pandas as pd
from connection import connect_to_influxdb
import warnings
from influxdb_client.client.warnings import MissingPivotFunction

# Deshabilitar advertencias de PivotFunction de InfluxDB
warnings.simplefilter("ignore", MissingPivotFunction)

# Función para enviar datos de temperatura, humedad y CO2 en tiempo real
async def send_sensor_data(websocket, client):
    """Envía datos de temperatura, humedad y CO2 en tiempo real a los clientes conectados."""

    print("Cliente conectado.")
    await websocket.send("Bienvenido al servidor de datos IoT. Recibiendo datos de temperatura, humedad y CO2.")

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

            if tables_temp.empty:
                print("No hay datos de temperatura en el rango de tiempo especificado.")
            else:
                if '_start' in tables_temp.columns and '_value' in tables_temp.columns:
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
                        last_timestamp = new_data_temp['Time'].max()
                        for _, row in new_data_temp.iterrows():
                            print(f"Enviando datos de temperatura: Tiempo: {row['Time']}, Temperatura: {row['temperature']}°C")
                            await websocket.send(f"Tiempo: {row['Time']}, Temperatura: {row['temperature']}°C")

                            # Verificar si la temperatura es mayor a 27°C y enviar una alerta
                            if row['temperature'] > 27:
                                alert_message = f"ALERTA: La temperatura ha superado los 27°C. Actual: {row['temperature']}°C"
                                await websocket.send(alert_message)

            # Consulta los últimos datos de humedad
            query_hum = f'''
            from(bucket: "farm_iot")
                |> range(start: -10s)
                |> filter(fn: (r) => r["_measurement"] == "humidity_sensor")
                |> filter(fn: (r) => r["_field"] == "value")
            '''
            tables_hum = query_api.query_data_frame(query_hum)

            if tables_hum.empty:
                print("No hay datos de humedad en el rango de tiempo especificado.")
            else:
                if '_start' in tables_hum.columns and '_value' in tables_hum.columns:
                    df_hum = tables_hum[['_start', '_value']].copy()
                    df_hum.loc[:, '_start'] = pd.to_datetime(df_hum['_start'])
                    df_hum.rename(columns={'_start': 'Time', '_value': 'humidity'}, inplace=True)

                    if last_timestamp is None:
                        new_data_hum = df_hum
                    else:
                        new_data_hum = df_hum[df_hum['Time'] > last_timestamp]

                    if new_data_hum.empty:
                        print("No hay datos nuevos de humedad para enviar.")
                    else:
                        last_timestamp = new_data_hum['Time'].max()
                        for _, row in new_data_hum.iterrows():
                            print(f"Enviando datos de humedad: Tiempo: {row['Time']}, Humedad: {row['humidity']}%")
                            await websocket.send(f"Tiempo: {row['Time']}, Humedad: {row['humidity']}%")

                            # Verificar si la humedad es mayor a 70% y enviar una alerta
                            if row['humidity'] > 70:
                                alert_message = f"ALERTA: La humedad ha superado el 70%. Actual: {row['humidity']}%"
                                await websocket.send(alert_message)

            # Consulta los últimos datos de CO2
            query_co2 = f'''
            from(bucket: "farm_iot")
                |> range(start: -10s)
                |> filter(fn: (r) => r["_measurement"] == "co2_sensor")
                |> filter(fn: (r) => r["_field"] == "value")
            '''
            tables_co2 = query_api.query_data_frame(query_co2)

            if tables_co2.empty:
                print("No hay datos de CO2 en el rango de tiempo especificado.")
            else:
                if '_start' in tables_co2.columns and '_value' in tables_co2.columns:
                    df_co2 = tables_co2[['_start', '_value']].copy()
                    df_co2.loc[:, '_start'] = pd.to_datetime(df_co2['_start'])
                    df_co2.rename(columns={'_start': 'Time', '_value': 'co2'}, inplace=True)

                    if last_timestamp is None:
                        new_data_co2 = df_co2
                    else:
                        new_data_co2 = df_co2[df_co2['Time'] > last_timestamp]

                    if new_data_co2.empty:
                        print("No hay datos nuevos de CO2 para enviar.")
                    else:
                        last_timestamp = new_data_co2['Time'].max()
                        for _, row in new_data_co2.iterrows():
                            print(f"Enviando datos de CO2: Tiempo: {row['Time']}, CO2: {row['co2']} ppm")
                            await websocket.send(f"Tiempo: {row['Time']}, CO2: {row['co2']} ppm")

                            # Verificar si el nivel de CO2 es mayor a 1000 ppm y enviar una alerta
                            if row['co2'] > 1000:
                                alert_message = f"ALERTA: El nivel de CO2 ha superado los 1000 ppm. Actual: {row['co2']} ppm"
                                await websocket.send(alert_message)

            await asyncio.sleep(5)  # Pausa entre consultas
    except websockets.exceptions.ConnectionClosed:
        print("Conexión cerrada con el cliente.")
    except Exception as e:
        print(f"Error inesperado: {e}")

# Configurar el servidor WebSocket
async def main():
    # Conectar correctamente a InfluxDB
    client = connect_to_influxdb()  # Esto ahora devuelve un objeto InfluxDBClient
    server = await websockets.serve(lambda ws, path: send_sensor_data(ws, client), "0.0.0.0", 8765)
    print("Servidor WebSocket iniciado en ws://0.0.0.0:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
