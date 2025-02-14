import redis
import json
from datetime import datetime, timedelta

# Conectar a Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Calcular el rango de tiempo para la última semana: desde hace 7 días hasta ahora.
end_time = datetime.now()
start_time = end_time - timedelta(weeks=1)

# Convertir los tiempos a epoch (segundos)
start_epoch = start_time.timestamp()
end_epoch = end_time.timestamp()

# Consultar el sorted set para obtener los registros dentro del rango de tiempo definido.
registros_bytes = r.zrangebyscore("sensor:values", start_epoch, end_epoch)

# Convertir cada registro de bytes a un diccionario de Python
registros = [json.loads(registro.decode('utf-8')) for registro in registros_bytes]

print("Datos de la última semana:")
for registro in registros:
    print(registro)
