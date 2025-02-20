import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from connection import connect_to_influxdb

client = connect_to_influxdb()

# Función para obtener los datos de temperatura
def get_temperature_data(client):
    """Recupera los datos de temperatura de los últimos 10 minutos."""
    query_api = client.query_api()

    # Consulta para obtener datos de temperatura
    query_temp = f'''
    from(bucket: "farm_iot")
        |> range(start: -10m)
        |> filter(fn: (r) => r["_measurement"] == "temperature_sensor")
        |> filter(fn: (r) => r["_field"] == "value")
        |> yield(name: "temperature_sensor")
    '''

    # Consulta a la base de datos
    tables_temp = query_api.query_data_frame(query_temp)

    # Verifica si hay datos de temperatura
    if tables_temp.empty:
        print("No se encontraron datos de temperatura.")
        return pd.DataFrame()

    # Convertir a DataFrame
    df_temp = tables_temp[['_time', '_value']].rename(columns={"_time": "Time", "_value": "Temperature"})
    
    # Convertir 'Time' a formato datetime y establecerlo como índice
    df_temp['Time'] = pd.to_datetime(df_temp['Time'])
    df_temp.set_index('Time', inplace=True)

    return df_temp

# Función para obtener los datos de humedad
def get_humidity_data(client):
    """Recupera los datos de humedad de los últimos 10 minutos."""
    query_api = client.query_api()

    # Consulta para obtener datos de humedad
    query_hum = f'''
    from(bucket: "farm_iot")
        |> range(start: -10m)
        |> filter(fn: (r) => r["_measurement"] == "humidity_sensor")
        |> filter(fn: (r) => r["_field"] == "value")
        |> yield(name: "humidity_sensor")
    '''

    # Consulta a la base de datos
    tables_hum = query_api.query_data_frame(query_hum)

    # Verifica si hay datos de humedad
    if tables_hum.empty:
        print("No se encontraron datos de humedad.")
        return pd.DataFrame()

    # Convertir a DataFrame
    df_hum = tables_hum[['_time', '_value']].rename(columns={"_time": "Time", "_value": "Humidity"})
    
    # Convertir 'Time' a formato datetime y establecerlo como índice
    df_hum['Time'] = pd.to_datetime(df_hum['Time'])
    df_hum.set_index('Time', inplace=True)

    return df_hum

# Función de actualización para las gráficas en tiempo real
def update(frame):
    """Actualiza las gráficas con los datos más recientes."""
    global ax_temp, ax_hum, line_temp, line_hum

    # Obtener datos actualizados
    df_temp = get_temperature_data(client)
    df_hum = get_humidity_data(client)

    if df_temp.empty or df_hum.empty:
        print("No se encontraron datos de temperatura o humedad.")
        return

    # Actualizar los datos de la gráfica de temperatura
    line_temp.set_data(df_temp.index, df_temp['Temperature'])
    
    # Actualizar los datos de la gráfica de humedad
    line_hum.set_data(df_hum.index, df_hum['Humidity'])

    # Ajustar límites del gráfico de temperatura
    ax_temp.relim()
    ax_temp.autoscale_view()

    # Ajustar límites del gráfico de humedad
    ax_hum.relim()
    ax_hum.autoscale_view()

    # Personalizar los gráficos
    ax_temp.set_title("Temperatura - Últimos 10 minutos")
    ax_temp.set_xlabel("Tiempo")
    ax_temp.set_ylabel("Temperatura (°C)")
    ax_temp.grid(True)

    ax_hum.set_title("Humedad - Últimos 10 minutos")
    ax_hum.set_xlabel("Tiempo")
    ax_hum.set_ylabel("Humedad (%)")
    ax_hum.grid(True)

    # Leyendas
    ax_temp.legend(["Temperatura (°C)"])
    ax_hum.legend(["Humedad (%)"])

# Función para crear y mostrar las gráficas en tiempo real
def plot_realtime_data():
    """Crea las gráficas en tiempo real para temperatura y humedad en gráficos separados."""
    global ax_temp, ax_hum, line_temp, line_hum

    # Configuración inicial de las gráficas
    fig, (ax_temp, ax_hum) = plt.subplots(2, 1, figsize=(10, 12))

    # Gráfica de temperatura
    line_temp, = ax_temp.plot([], [], marker='o', linestyle='-', color='b')

    # Gráfica de humedad
    line_hum, = ax_hum.plot([], [], marker='x', linestyle='-', color='g')

    # Crear animación en tiempo real
    ani = FuncAnimation(fig, update, interval=5000)  # Actualiza cada 5 segundos

    plt.tight_layout()
    plt.show()

# Ejecutar la función para crear y mostrar las gráficas
plot_realtime_data()