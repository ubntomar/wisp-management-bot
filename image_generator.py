import redis
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Conexión a Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Rango de las últimas 24 horas
end_time = datetime.now()
start_time = end_time - timedelta(hours=24)

start_epoch = start_time.timestamp()
end_epoch = end_time.timestamp()

# Recuperar registros de las últimas 24 horas
registros_bytes = r.zrangebyscore("sensor:values", start_epoch, end_epoch)

tiempos = []
voltajes = []

for registro_b in registros_bytes:
    try:
        registro_str = registro_b.decode('utf-8')
        registro = json.loads(registro_str)
        
        if "timestamp" in registro and "voltage" in registro:
            # Convertir el timestamp a objeto datetime
            dt = datetime.strptime(registro["timestamp"], "%Y-%m-%d %H:%M:%S")
            tiempos.append(dt)
            voltajes.append(float(registro["voltage"]))
    except Exception as e:
        print("Error procesando un registro:", e)

if tiempos and voltajes:
    # Crear la figura
    plt.figure(figsize=(12, 6))
    plt.plot(tiempos, voltajes, marker='o', linestyle='-', color='b', label="Voltaje")
    plt.title("Voltaje vs. Tiempo (Últimas 24 horas)")
    plt.xlabel("Tiempo")
    plt.ylabel("Voltaje")
    plt.grid(True)
    
    ax = plt.gca()
    
    # Forzar a que el eje X muestre desde start_time hasta end_time
    ax.set_xlim([start_time, end_time])

    # **Ajustar el eje Y para que muestre entre 20V y 30V**
    ax.set_ylim([20, 30])

    # Mostrar marcas de hora cada 1 hora
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    
    # **Formato de 12 horas AM/PM**
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%I:%M %p'))

    plt.gcf().autofmt_xdate()  # Rotar etiquetas para mejor lectura
    
    # **Mostrar valores en el primer y último punto**
    plt.annotate(f"{voltajes[0]:.2f}V",  # Primer punto
                 (tiempos[0], voltajes[0]), 
                 textcoords="offset points", 
                 xytext=(0, 10),  # Mover hacia arriba
                 ha='center', 
                 fontsize=10, 
                 color='green',
                 fontweight='bold')

    plt.annotate(f"{voltajes[-1]:.2f}V",  # Último punto
                 (tiempos[-1], voltajes[-1]), 
                 textcoords="offset points", 
                 xytext=(0, 10),  # Mover hacia arriba
                 ha='center', 
                 fontsize=10, 
                 color='green',
                 fontweight='bold')

    # **Anotaciones para los puntos más bajos**
    min_threshold = min(voltajes) + 0.2  # Consideramos los más bajos cercanos al mínimo +0.2V
    for i in range(len(voltajes)):
        if voltajes[i] <= min_threshold:  # Filtrar puntos bajos
            plt.annotate(f"{voltajes[i]:.2f}V", 
                         (tiempos[i], voltajes[i]), 
                         textcoords="offset points", 
                         xytext=(0, -15),  # Ajuste para que el texto no se sobreponga
                         ha='center', 
                         fontsize=10, 
                         color='red')

    plt.tight_layout()
    
    # Guardar la gráfica en PNG
    nombre_imagen = "img/voltage_last24hours.png"
    plt.savefig(nombre_imagen)
    plt.close()
    print(f"Gráfica guardada en {nombre_imagen}")
else:
    print("No hay datos en las últimas 24 horas o no cumplen con el formato esperado.")
