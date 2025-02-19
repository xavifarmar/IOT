import pandas as pd
import matplotlib.pyplot as plt
from connection_component import InfluxDBConnection

def plot_temperature_data():
    """Recupera y grafica los datos de temperatura de los últimos 10 minutos."""
    connection = InfluxDBConnection(
        url="http://192.168.105.110:8086",
        token="ejmO_FbDgQVx_OMFFLxO8cEjYpPzZx_QdMEy0VHpSSr3DC7idArwcj1CSvhqyBG_alzh72D8Xd7sGDEtjkBjsg==",
        org="jmh",
        bucket="jmh"
    )
    client = connection.get_client()
    query_api = connection.get_query_api(client)

    query = f'''
    from(bucket: "{connection.bucket}")
        |> range(start: -10m)
        |> filter(fn: (r) => r._measurement == "thermometer" and r._field == "temperature")
        |> yield(name: "temperature_data")
    '''

    # Ejecutar la consulta
    tables = query_api.query_data_frame(query)
    if tables.empty:
        print("No se encontraron datos de temperatura.")
        return

    # Convertir a DataFrame
    df = tables[['_time', '_value']].rename(columns={"_time": "Time", "_value": "Temperature"})
    df['Time'] = pd.to_datetime(df['Time'])
    df.set_index('Time', inplace=True)

    # Graficar los datos
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['Temperature'], marker='o', linestyle='-', color='b')
    plt.title("Temperatura del Termómetro - Últimos 10 minutos")
    plt.xlabel("Tiempo")
    plt.ylabel("Temperatura (°C)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_temperature_data()
