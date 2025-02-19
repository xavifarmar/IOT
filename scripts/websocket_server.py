import asyncio
import websockets

# Lista de clientes WebSocket conectados
connected_clients = set()

# Función para manejar la conexión WebSocket
async def handler(websocket, path):
    
    # Agregar el cliente a la lista de clientes conectados
    connected_clients.add(websocket)
    print(f"Nuevo cliente conectado: {websocket.remote_address}")

    try:
        # Mantener la conexión abierta, esperando cualquier mensaje
        while True:
            # Esperamos recibir algún mensaje del cliente
            message = await websocket.recv()
            print(f"Mensaje recibido del cliente: {message}")
    except websockets.exceptions.ConnectionClosed:
        print(f"Cliente desconectado: {websocket.remote_address}")
    finally:
        # Eliminar el cliente de la lista cuando se desconecte
        connected_clients.remove(websocket)

# Función para enviar mensajes a todos los clientes conectados
async def broadcast(message):
    # Enviar el mensaje a todos los clientes conectados
    for client in connected_clients:
        try:
            await client.send(message)
        except websockets.exceptions.ConnectionClosed:
            connected_clients.remove(client)

# Crear el servidor WebSocket
async def start_websocket_server():
    server = await websockets.serve(handler, "localhost", 8765)
    await server.wait_closed()
