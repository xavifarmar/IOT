import asyncio
import websockets

async def receive_data():

    uri = "ws://10.0.2.15:8765"

    async with websockets.connect(uri) as websocket:
        print(f"Conectado al servidor WebSocket: {uri}")
        try:
            while True:
                message = await websocket.recv()
                print(f"Datos recibidos: {message}")
        except websockets.exceptions.ConnectionClosed:
            print("Conexión cerrada por el servidor.")

if __name__ == "__main__":
    asyncio.run(receive_data())
