import requests
import redis
import json
from datetime import datetime
import sys

# Conectar a Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Configuración de sensores por ubicación
SENSORES = {
    "Montecristo": {
        "url": "http://192.168.21.253:8013/50",
        "method": "GET",
        "value_key": "data.sensor1"  # Ruta para extraer el valor del JSON
    },
    "Retiro": {
        "url": "http://192.168.21.253:8013/50",  # Misma URL por ahora, actualizar según corresponda
        "method": "GET",
        "value_key": "data.sensor1"
    }
    # Agregar más ubicaciones según sea necesario
}

def get_nested_value(data, path):
    """Obtiene un valor anidado en un diccionario según una ruta con notación de puntos"""
    keys = path.split('.')
    value = data
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value

def obtener_datos_sensor(ubicacion):
    """Obtiene datos del sensor para una ubicación específica"""
    if ubicacion not in SENSORES:
        print(f"Error: La ubicación '{ubicacion}' no está configurada")
        return False
    
    config = SENSORES[ubicacion]
    try:
        if config["method"] == "GET":
            response = requests.get(config["url"], timeout=10)
        else:
            # Implementar otros métodos si es necesario (POST, etc.)
            print(f"Error: Método '{config['method']}' no implementado")
            return False
        
        if response.status_code != 200:
            print(f"Error en la solicitud: Código de estado {response.status_code}")
            return False
            
        json_response = response.json()
        
        # Extraer el valor según la ruta configurada
        sensor_value = get_nested_value(json_response, config["value_key"])
        
        if sensor_value is None:
            print(f"No se encontró el valor en la ruta '{config['value_key']}' en la respuesta")
            return False
            
        try:
            voltage = float(sensor_value)
        except ValueError:
            print(f"El valor '{sensor_value}' no se puede convertir a float")
            voltage = sensor_value  # Se asigna directamente si no es convertible
        
        # Obtener el timestamp actual
        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Crear el registro
        registro = {
            "timestamp": timestamp_str,
            "voltage": voltage,
            "location": ubicacion
        }
        
        # Convertir el registro a JSON
        registro_json = json.dumps(registro)
        
        # Usar ubicación en la clave para separar los datos
        key = f"sensor:values:{ubicacion.lower()}"
        
        # Utilizar el timestamp en formato epoch como score
        score = now.timestamp()
        r.zadd(key, {registro_json: score})
        
        print(f"Registro para {ubicacion} agregado correctamente:")
        print(registro)
        return True
        
    except Exception as e:
        print(f"Error al obtener datos para {ubicacion}: {str(e)}")
        return False

def main():
    # Si se proporciona una ubicación específica como argumento
    if len(sys.argv) > 1:
        ubicacion = sys.argv[1]
        if ubicacion in SENSORES:
            obtener_datos_sensor(ubicacion)
        else:
            print(f"Ubicación '{ubicacion}' no encontrada. Ubicaciones disponibles: {list(SENSORES.keys())}")
    else:
        # Procesar todas las ubicaciones
        for ubicacion in SENSORES:
            print(f"Procesando datos para: {ubicacion}")
            obtener_datos_sensor(ubicacion)

if __name__ == "__main__":
    main()