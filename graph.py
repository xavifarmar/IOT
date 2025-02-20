import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from connection import connect_to_influxdb


client = connect_to_influxdb()

# Función para simular la lectura de humedad

def get_sensor_data(client):
    
    """Recupera los datos de temperatura y humedad de los últimos 10 minutos."""
    query_api = client.get_query_api(client)

    query = f'''
    from(bucket: "{"farm_iot"}")
        |> range(start: -10m)
        |> filter(fn: (r) => r._measurement == "temperature_sensor" and r._field == "value")
        |> filter(fn: (r) => r._measurement == "humidity_sensor" and r._field == "value")
        |> pivot(rowKey:["_time"], columnKey:["_measurement"], valueColumn:"_value")
        |> yield(name: "sensor_data")
    '''
    tables = query_api.query_data_frame(query)
    if tables.empty:
        return pd.DataFrame()  # Devuelve un DataFrame vacío si no hay datos

    # Convertir a DataFrame
    df = tables[['_time', 'temperature_sensor', 'humidity_sensor']].rename(columns={
        "_time": "Time", 
        "temperature_sensor": "Temperature", 
        "humidity_sensor": "Humidity"
    })
    df['Time'] = pd.to_datetime(df['Time'])
    df.set_index('Time', inplace=True)
    return df

def update(frame):
    """Función de actualización para la gráfica en tiempo real."""
    global ax, line_temp, line_hum

    # Obtener datos actualizados
    df = get_sensor_data()
    if df.empty:
        print("No se encontraron datos de temperatura o humedad.")
        return

    # Actualizar los datos de la gráfica
    line_temp.set_data(df.index, df['Temperature'])
    line_hum.set_data(df.index, df['Humidity'])

    # Ajustar límites del gráfico según los datos
    ax.relim()
    ax.autoscale_view()

    # Personalizar el gráfico
    ax.set_title("Temperatura y Humedad - Últimos 10 minutos")
    ax.set_xlabel("Tiempo")
    ax.set_ylabel("Valor")
    ax.grid(True)
    ax.legend(["Temperatura (°C)", "Humedad (%)"])

def plot_realtime_data():
    """Crea la gráfica en tiempo real para temperatura y humedad."""
    global ax, line_temp, line_hum

    # Configuración inicial de la gráfica
    fig, ax = plt.subplots(figsize=(10, 6))
    line_temp, = ax.plot([], [], marker='o', linestyle='-', color='b')
    line_hum, = ax.plot([], [], marker='x', linestyle='-', color='g')

    # Crear animación en tiempo real
    ani = FuncAnimation(fig, update, interval=5000)  # Actualiza cada 5 segundos
    plt.show()


plot_realtime_data()
