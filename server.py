import asyncio
import websockets
import pandas as pd
from connection import connect_to_influxdb

# Función para enviar datos de temperatura en tiempo real
async def send_temperature_data(websocket, client):
    """Envía datos de temperatura en tiempo real a los clientes conectados."""

    # Enviar un mensaje de bienvenida cuando un cliente se conecta
    print("Cliente conectado.")
    await websocket.send("Bienvenido al servidor de datos IoT. Recibiendo datos de temperatura y humedad.")

    # Asegúrate de que 'client' sea el objeto correcto de InfluxDBClient
    query_api = client.query_api()  # Obtén el query_api correctamente

    last_timestamp = None  # Almacena el último timestamp enviado

    try:
        while True:
            # Consulta los últimos datos de temperatura con pivot()
            query_temp = f'''
            from(bucket: "farm_iot")
                |> range(start: -10s)
                |> filter(fn: (r) => r["_measurement"] == "temperature_sensor")
                |> filter(fn: (r) => r["_field"] == "value")
                |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")
            '''
            tables_temp = query_api.query_data_frame(query_temp)

            # Consulta los últimos datos de humedad con pivot()
            query_hum = f'''
            from(bucket: "farm_iot")
                |> range(start: -10s)
                |> filter(fn: (r) => r["_measurement"] == "humidity_sensor")
                |> filter(fn: (r) => r["_field"] == "value")
                |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")
            '''
            tables_hum = query_api.query_data_frame(query_hum)

            # Verificar si las columnas están presentes antes de acceder a ellas
            if not tables_temp.empty:
                # Comprueba las columnas y usa el nombre correcto
                if 'Time' in tables_temp.columns and 'temperature_sensor' in tables_temp.columns:
                    df_temp = tables_temp[['Time', 'temperature_sensor']]
                    df_temp['Time'] = pd.to_datetime(df_temp['Time'])

                    # Evitar que se envíen datos con el mismo timestamp
                    if last_timestamp is None:
                        new_data_temp = df_temp
                    else:
                        new_data_temp = df_temp[df_temp['Time'] > last_timestamp]

                    if not new_data_temp.empty:
                        last_timestamp = new_data_temp['Time'].max()
                        # Enviar datos nuevos de temperatura
                        for _, row in new_data_temp.iterrows():
                            await websocket.send(
                                f"Tiempo: {row['Time']}, Temperatura: {row['temperature_sensor']}°C"
                            )
                        print( f"Tiempo: {row['Time']}, Temperatura: {row['temperature_sensor']}°C")
            if not tables_hum.empty:
                # Comprueba las columnas y usa el nombre correcto
                if 'Time' in tables_hum.columns and 'humidity_sensor' in tables_hum.columns:
                    df_hum = tables_hum[['Time', 'humidity_sensor']]
                    df_hum['Time'] = pd.to_datetime(df_hum['Time'])

                    # Evitar que se envíen datos con el mismo timestamp
                    if last_timestamp is None:
                        new_data_hum = df_hum
                    else:
                        new_data_hum = df_hum[df_hum['Time'] > last_timestamp]

                    if not new_data_hum.empty:
                        last_timestamp = new_data_hum['Time'].max()
                        # Enviar datos nuevos de humedad
                        for _, row in new_data_hum.iterrows():
                            await websocket.send(
                                f"Tiempo: {row['Time']}, Humedad: {row['humidity_sensor']}%"
                            )
                    print(f"Tiempo: {row['Time']}, Humedad: {row['humidity_sensor']}%")
            await asyncio.sleep(5)  # Pausa entre consultas
    except websockets.exceptions.ConnectionClosed:
        print("Conexión cerrada con el cliente.")

# Configurar el servidor WebSocket
async def main():
    # Conectar correctamente a InfluxDB
    client = connect_to_influxdb()  # Esto ahora devuelve un objeto InfluxDBClient
    server = await websockets.serve(lambda ws, path: send_temperature_data(ws, client), "0.0.0.0", 8765)
    print("Servidor WebSocket iniciado en ws://0.0.0.0:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
