import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from connection_component import InfluxDBConnection

def get_temperature_data():
    """Recupera los datos de temperatura de los últimos 10 minutos."""
    connection = InfluxDBConnection(
        url="http://10.0.2.15:8086",
        token="Obzc66q1bvHbtsbH1claJPfnhcrGV51-P9cCf-1RNE5zcuR4z0XX1z-3N3_YI6kVIJwtS6bTmlCKUbMLGZIraA==",
        org="xfm",
        bucket="xfm"
    )
    client = connection.get_client()
    query_api = connection.get_query_api(client)

    query = f'''
    from(bucket: "{connection.bucket}")
        |> range(start: -10m)
        |> filter(fn: (r) => r._measurement == "thermometer" and r._field == "temperature")
        |> yield(name: "temperature_data")
    '''
    tables = query_api.query_data_frame(query)
    if tables.empty:
        return pd.DataFrame()  # Devuelve un DataFrame vacío si no hay datos

    # Convertir a DataFrame
    df = tables[['_time', '_value']].rename(columns={"_time": "Time", "_value": "Temperature"})
    df['Time'] = pd.to_datetime(df['Time'])
    df.set_index('Time', inplace=True)
    return df

def update(frame):
    """Función de actualización para la gráfica en tiempo real."""
    global ax, line

    # Obtener datos actualizados
    df = get_temperature_data()
    if df.empty:
        print("No se encontraron datos de temperatura.")
        return

    # Actualizar los datos de la gráfica
    ax.clear()
    ax.plot(df.index, df['Temperature'], marker='o', linestyle='-', color='b')

    # Personalizar el gráfico
    ax.set_title("Temperatura del Termómetro - Últimos 10 minutos")
    ax.set_xlabel("Tiempo")
    ax.set_ylabel("Temperatura (°C)")
    ax.grid(True)

def plot_realtime_temperature():
    """Crea la gráfica en tiempo real."""
    global ax, line

    # Configuración inicial de la gráfica
    fig, ax = plt.subplots(figsize=(10, 6))
    line, = ax.plot([], [], marker='o', linestyle='-', color='b')

    # Crear animación en tiempo real
    ani = FuncAnimation(fig, update, interval=5000)  # Actualiza cada 5 segundos
    plt.show()

if __name__ == "__main__":
    plot_realtime_temperature()
