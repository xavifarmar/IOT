import threading
from connection import connect_to_influxdb
from sensors.thermo_01 import temperature_sensor
from sensors.sensor_co2 import co2_sensor
from sensors.humidity_01 import humidity_sensor


def main():
    # Obtener el cliente de InfluxDB
    client = connect_to_influxdb()
    
    # Crear hilos para cada sensor
    thread_1 = threading.Thread(target=temperature_sensor, args=(client,))
    thread_2 = threading.Thread(target=co2_sensor, args=(client,))
    thread_3 = threading.Thread(target=humidity_sensor, args=(client,))

    # Iniciar los hilos
    thread_1.start()
    thread_2.start()
    thread_3.start()
    
    # Mantener el hilo principal activo para que los hilos continúen corriendo
    thread_1.join()
    thread_2.join()
    thread_3.join()

if __name__ == "__main__":
    main()




