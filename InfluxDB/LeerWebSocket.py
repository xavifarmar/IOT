import asyncio
import websockets

async def receive_data():
    uri = "ws://192.168.105.110:8765"  # Cambia la IP al servidor WebSocket
    

    async with websockets.connect(uri) as websocket:
        print("Conectado al servidor WebSocket")
        try:
            while True:
                message = await websocket.recv()
                print(f"Datos recibidos: {message}")
        except websockets.exceptions.ConnectionClosed:
            print("Conexión cerrada por el servidor.")

if __name__ == "__main__":
    asyncio.run(receive_data())
