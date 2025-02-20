import asyncio
import websockets
import pandas as pd
from connection import connect_to_influxdb

# Función para enviar datos de temperatura en tiempo real
async def send_temperature_data(websocket, client):
    """Envía datos de temperatura en tiempo real a los clientes conectados."""
    
    # Asegúrate de que 'client' sea el objeto correcto de InfluxDBClient
    query_api = client.query_api()  # Obtén el query_api correctamente

    last_timestamp = None  # Almacena el último timestamp enviado

    try:
        while True:
            # Consulta los últimos datos
            query = f'''
            from(bucket: "farm_iot")
                |> range(start: -10m)
                |> filter(fn: (r) => r._measurement == "temperature_sensor" and r._field == "value")
                |> filter(fn: (r) => r._measurement == "humidity_sensor" and r._field == "value")
                |> pivot(rowKey:["_time"], columnKey:["_measurement"], valueColumn:"_value")
            '''
            tables = query_api.query_data_frame(query)
            
            # Procesar nuevos datos
            if not tables.empty:
                df = tables[['Time', 'temperature_sensor', 'humidity_sensor']]
                df['Time'] = pd.to_datetime(df['Time'])
                new_data = df[df['Time'] > (last_timestamp or df['Time'].min())]

                if not new_data.empty:
                    last_timestamp = new_data['Time'].max()
                    # Enviar datos nuevos a través del WebSocket
                    for _, row in new_data.iterrows():
                         await websocket.send(
                         f"Tiempo: {row['Time']}, Temperatura: {row['temperature_sensor']}°C, Humedad: {row['humidity_sensor']}%"
                         )
            
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
