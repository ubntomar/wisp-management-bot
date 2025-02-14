import requests
import redis
import json
from datetime import datetime

# Conectar a Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# URL de la solicitud GET
url = "http://192.168.21.253:8013/50"

# Realizar la solicitud GET
response = requests.get(url)

if response.status_code == 200:
    json_response = response.json()
    data = json_response.get("data", {})
    
    # Extraer el valor de sensor1 y convertirlo a float
    sensor1_value = data.get("sensor1")
    
    if sensor1_value is None:
        print("No se encontró el valor de sensor1 en la respuesta.")
    else:
        try:
            voltage = float(sensor1_value)
        except ValueError:
            print("El valor de sensor1 no se puede convertir a float.")
            voltage = sensor1_value  # Se asigna directamente si no es convertible
        
        # Obtener el timestamp actual en el formato deseado
        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Crear el registro con el formato requerido
        registro = {
            "timestamp": timestamp_str,
            "voltage": voltage
        }
        
        # Convertir el registro a JSON
        registro_json = json.dumps(registro)
        
        # Utilizar el timestamp en formato epoch como score en el sorted set
        score = now.timestamp()
        r.zadd("sensor:values", {registro_json: score})
        
        print("Registro agregado correctamente:")
        print(registro)
else:
    print(f"Error en la solicitud GET: Código de estado {response.status_code}")
