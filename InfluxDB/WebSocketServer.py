import asyncio
import websockets
import pandas as pd
from connection_component import InfluxDBConnection

async def send_temperature_data(websocket, path):
    """Envía datos de temperatura en tiempo real a los clientes conectados."""
    connection = InfluxDBConnection(
        url="http://localhost:8086",
        token="ejmO_FbDgQVx_OMFFLxO8cEjYpPzZx_QdMEy0VHpSSr3DC7idArwcj1CSvhqyBG_alzh72D8Xd7sGDEtjkBjsg==",
        org="jmh",
        bucket="jmh"
    )

    client = connection.get_client()
    query_api = connection.get_query_api(client)

    last_timestamp = None  # Almacena el último timestamp enviado

    try:
        while True:
            # Consulta los últimos datos
            query = f'''
            from(bucket: "{connection.bucket}")
                |> range(start: -10s)
                |> filter(fn: (r) => r._measurement == "thermometer" and r._field == "temperature")
            '''
            tables = query_api.query_data_frame(query)
            
            # Procesar nuevos datos
            if not tables.empty:
                df = tables[['_time', '_value']].rename(columns={"_time": "Time", "_value": "Temperature"})
                df['Time'] = pd.to_datetime(df['Time'])
                new_data = df[df['Time'] > (last_timestamp or df['Time'].min())]

                if not new_data.empty:
                    last_timestamp = new_data['Time'].max()
                    # Enviar datos nuevos a través del WebSocket
                    for _, row in new_data.iterrows():
                        await websocket.send(f"Tiempo: {row['Time']}, Temperatura: {row['Temperature']}°C")
            
            await asyncio.sleep(5)  # Pausa entre consultas
    except websockets.exceptions.ConnectionClosed:
        print("Conexión cerrada con el cliente.")

# Configurar el servidor WebSocket
async def main():
    server = await websockets.serve(send_temperature_data, "0.0.0.0", 8765)
    print("Servidor WebSocket iniciado en ws://0.0.0.0:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
