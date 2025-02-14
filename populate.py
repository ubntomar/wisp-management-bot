import redis
import random
import json
from datetime import datetime, timedelta

# Conectar a Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Clave del sorted set donde se almacenarán los datos
key = "sensor:values"

# Definir la fecha de inicio y fin (10 al 12 de febrero de este mes, por ejemplo 2025)
start_time = datetime(2025, 2, 10, 0, 0, 0)
end_time   = datetime(2025, 2, 12, 23, 30, 0)

current_time = start_time

while current_time <= end_time:
    # Generar un voltaje aleatorio entre 24 y 27, redondeado a 2 decimales
    voltage = round(random.uniform(24, 27), 2)
    
    # Formatear el timestamp
    timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Crear el registro con la fecha y el voltaje
    registro = {
        "timestamp": timestamp_str,
        "voltage": voltage
    }
    
    # Convertir el registro a JSON
    registro_json = json.dumps(registro)
    
    # Convertir el timestamp a epoch para usarlo como score en el sorted set
    epoch_time = current_time.timestamp()
    
    # Almacenar el registro en Redis
    r.zadd(key, {registro_json: epoch_time})
    
    # Incrementar el tiempo en 30 minutos
    current_time += timedelta(minutes=30)

print("Datos de prueba generados en Redis.")
