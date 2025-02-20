import asyncio
import websockets
import pandas as pd
from connection import connect_to_influxdb


client = connect_to_influxdb()
async def control_actuators(websocket):
    """Activa o desactiva actuadores en función de los datos de los sensores."""
    

    client = client.get_client()
    query_api = client.get_query_api(client)

    last_timestamp = None  # Almacena el último timestamp enviado

    try:
        while True:
            # Consulta los datos de los sensores
            query = '''
            from(bucket: "{connection.bucket}")
                |> range(start: -10s)
                |> filter(fn: (r) => r._measurement == "temperature_sensor" and r._field == "value")
                |> filter(fn: (r) => r._measurement == "humidity_sensor" and r._field == "value")
                |> pivot(rowKey:["_time"], columnKey:["_measurement"], valueColumn:"_value")
            '''
            tables = query_api.query_data_frame(query)

            if not tables.empty:
                df = tables[['Time', 'temperature_sensor', 'humidity_sensor']]
                df['Time'] = pd.to_datetime(df['Time'])
                new_data = df[df['Time'] > (last_timestamp or df['Time'].min())]

                if not new_data.empty:
                    last_timestamp = new_data['Time'].max()
                    for _, row in new_data.iterrows():
                        # Evaluar los datos y decidir qué hacer con los actuadores
                        temperature = row['temperature_sensor']
                        humidity = row['humidity_sensor']

                        # Ejemplo de reglas:
                        if temperature > 30:
                            # Actuar sobre el ventilador (Ejemplo: encender ventilador)
                            await websocket.send(f"Activando ventilador, temperatura: {temperature}°C")
                            # Código para activar el ventilador (puedes usar una API o hardware como MQTT)
                        elif temperature < 20:
                            # Actuar sobre el ventilador (Ejemplo: apagar ventilador)
                            await websocket.send(f"Desactivando ventilador, temperatura: {temperature}°C")

                        if humidity < 40:
                            # Actuar sobre el nebulizador (Ejemplo: activar nebulizador)
                            await websocket.send(f"Activando nebulizador, humedad: {humidity}%")
                        elif humidity > 60:
                            # Actuar sobre el nebulizador (Ejemplo: desactivar nebulizador)
                            await websocket.send(f"Desactivando nebulizador, humedad: {humidity}%")
            
            await asyncio.sleep(5)  # Pausa entre consultas
    except websockets.exceptions.ConnectionClosed:
        print("Conexión cerrada con el cliente.")

# Iniciar el servidor WebSocket
async def main():
    server = await websockets.serve(control_actuators, "0.0.0.0", 8765)
    print("Servidor WebSocket iniciado en ws://0.0.0.0:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
