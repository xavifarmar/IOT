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

# Función para obtener los datos de CO2
def get_co2_data(client):
    """Recupera los datos de CO2 de los últimos 10 minutos."""
    query_api = client.query_api()

    # Consulta para obtener datos de CO2
    query_co2 = f'''
    from(bucket: "farm_iot")
        |> range(start: -10m)
        |> filter(fn: (r) => r["_measurement"] == "co2_sensor")
        |> filter(fn: (r) => r["_field"] == "value")
        |> yield(name: "co2_sensor")
    '''

    # Consulta a la base de datos
    tables_co2 = query_api.query_data_frame(query_co2)

    # Verifica si hay datos de CO2
    if tables_co2.empty:
        print("No se encontraron datos de CO2.")
        return pd.DataFrame()

    # Convertir a DataFrame
    df_co2 = tables_co2[['_time', '_value']].rename(columns={"_time": "Time", "_value": "CO2"})
    
    # Convertir 'Time' a formato datetime y establecerlo como índice
    df_co2['Time'] = pd.to_datetime(df_co2['Time'])
    df_co2.set_index('Time', inplace=True)

    return df_co2

# Función de actualización para las gráficas en tiempo real
def update(frame):
    """Actualiza las gráficas con los datos más recientes."""
    global ax_temp, ax_hum, ax_co2, line_temp, line_hum, line_co2

    # Obtener datos actualizados
    df_temp = get_temperature_data(client)
    df_hum = get_humidity_data(client)
    df_co2 = get_co2_data(client)

    if df_temp.empty or df_hum.empty or df_co2.empty:
        print("No se encontraron datos de temperatura, humedad o CO2.")
        return

    # Actualizar los datos de la gráfica de temperatura
    line_temp.set_data(df_temp.index, df_temp['Temperature'])
    
    # Actualizar los datos de la gráfica de humedad
    line_hum.set_data(df_hum.index, df_hum['Humidity'])

    # Actualizar los datos de la gráfica de CO2
    line_co2.set_data(df_co2.index, df_co2['CO2'])

    # Ajustar límites del gráfico de temperatura
    ax_temp.relim()
    ax_temp.autoscale_view()

    # Ajustar límites del gráfico de humedad
    ax_hum.relim()
    ax_hum.autoscale_view()

    # Ajustar límites del gráfico de CO2
    ax_co2.relim()
    ax_co2.autoscale_view()

    # Personalizar los gráficos
    ax_temp.set_title("Temperatura - Últimos 10 minutos")
    ax_temp.set_xlabel("Tiempo")
    ax_temp.set_ylabel("Temperatura (°C)")
    ax_temp.grid(True)

    ax_hum.set_title("Humedad - Últimos 10 minutos")
    ax_hum.set_xlabel("Tiempo")
    ax_hum.set_ylabel("Humedad (%)")
    ax_hum.grid(True)

    ax_co2.set_title("CO2 - Últimos 10 minutos")
    ax_co2.set_xlabel("Tiempo")
    ax_co2.set_ylabel("CO2 (ppm)")
    ax_co2.grid(True)

    # Leyendas
    ax_temp.legend(["Temperatura (°C)"])
    ax_hum.legend(["Humedad (%)"])
    ax_co2.legend(["CO2 (ppm)"])

# Función para crear y mostrar las gráficas en tiempo real
def plot_realtime_data():
    """Crea las gráficas en tiempo real para temperatura, humedad y CO2 en gráficos separados."""
    global ax_temp, ax_hum, ax_co2, line_temp, line_hum, line_co2

    # Configuración inicial de las gráficas
    fig, (ax_temp, ax_hum, ax_co2) = plt.subplots(3, 1, figsize=(10, 18))

    # Gráfica de temperatura
    line_temp, = ax_temp.plot([], [], marker='o', linestyle='-', color='b')

    # Gráfica de humedad
    line_hum, = ax_hum.plot([], [], marker='x', linestyle='-', color='g')

    # Gráfica de CO2
    line_co2, = ax_co2.plot([], [], marker='s', linestyle='-', color='r')

    # Crear animación en tiempo real
    ani = FuncAnimation(fig, update, interval=5000)  # Actualiza cada 5 segundos

    plt.tight_layout()
    plt.show()

# Ejecutar la función para crear y mostrar las gráficas
plot_realtime_data()
