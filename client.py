import asyncio
import websockets

async def receive_data():
    uri = "ws://10.0.2.15:8765"  # Cambia la IP si es necesario

    try:
        print(f"Conectando al servidor WebSocket: {uri}")
        async with websockets.connect(uri) as websocket:
            print(f"Conectado al servidor WebSocket: {uri}")
            
            await asyncio.sleep(5)  # Espera un poco para asegurarse de que el servidor esté enviando datos

            while True:
                # Recibe el mensaje del servidor
                message = await websocket.recv()
                print(f"{message}")
    except websockets.exceptions.ConnectionClosed:
        print("Conexión cerrada por el servidor.")
    except Exception as e:
        print(f"Error al intentar conectar al servidor WebSocket: {e}")

if __name__ == "__main__":
    asyncio.run(receive_data())
