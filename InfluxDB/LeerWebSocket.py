import asyncio
import websockets

async def receive_data():
    uri = "ws://10.0.2.15:8765"  # Cambia la IP al servidor WebSocket

    try:
        async with websockets.connect(uri) as websocket:
            print("Conectado al servidor WebSocket")
            try:
                while True:
                    message = await websocket.recv()  # Recibe un mensaje del servidor
                    print(f"Datos recibidos: {message}")  # Imprime los datos recibidos

            except websockets.exceptions.ConnectionClosed:
                print("Conexión cerrada por el servidor.")

    except Exception as e:
        print(f"Error al intentar conectarse al servidor: {e}")

if __name__ == "__main__":
    asyncio.run(receive_data())
