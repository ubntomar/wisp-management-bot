import redis
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import sys
import os

# Ubicaciones disponibles
UBICACIONES = ["Montecristo", "Retiro"]  # Agregar más según sea necesario

# Directorio para guardar las imágenes
IMG_DIR = "/home/omar/whatssapp/wisp-management-bot/img"

def generar_grafica_voltaje(ubicacion):
    """Genera una gráfica de voltaje para la ubicación especificada"""
    print(f"Generando gráfica para {ubicacion}...")
    
    # Conexión a Redis
    r = redis.Redis(host='localhost', port=6379, db=0)
    
    # Clave específica para esta ubicación
    key = f"sensor:values:{ubicacion.lower()}"
    
    # Rango de las últimas 24 horas
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    start_epoch = start_time.timestamp()
    end_epoch = end_time.timestamp()
    
    # Recuperar registros de las últimas 24 horas para esta ubicación
    registros_bytes = r.zrangebyscore(key, start_epoch, end_epoch)
    
    if not registros_bytes:
        print(f"No hay datos para {ubicacion} en las últimas 24 horas")
        return False
    
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
            print(f"Error procesando un registro: {e}")
    
    if not tiempos or not voltajes:
        print(f"No se pudieron extraer datos válidos para {ubicacion}")
        return False
    
    # Crear la figura
    plt.figure(figsize=(12, 6))
    plt.plot(tiempos, voltajes, marker='o', linestyle='-', color='b', label="Voltaje")
    
    # Título que incluye la ubicación
    plt.title(f"Voltaje vs. Tiempo - {ubicacion} (Últimas 24 horas)")
    plt.xlabel("Tiempo")
    plt.ylabel("Voltaje")
    plt.grid(True)
    
    ax = plt.gca()
    
    # Forzar a que el eje X muestre desde start_time hasta end_time
    ax.set_xlim([start_time, end_time])
    
    # Ajustar el eje Y para que muestre entre 20V y 30V con espacio adicional abajo para el recuadro
    ax.set_ylim([20, 30])
    
    # Mostrar marcas de hora cada 1 hora
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    
    # Formato de 12 horas AM/PM
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%I:%M %p'))
    
    plt.gcf().autofmt_xdate()  # Rotar etiquetas para mejor lectura
    
    # Mostrar valores en el primer y último punto
    plt.annotate(f"{voltajes[0]:.2f}V",  # Primer punto
                 (tiempos[0], voltajes[0]), 
                 textcoords="offset points", 
                 xytext=(0, 10),
                 ha='center', 
                 fontsize=10, 
                 color='green',
                 fontweight='bold')
    
    plt.annotate(f"{voltajes[-1]:.2f}V",  # Último punto
                 (tiempos[-1], voltajes[-1]), 
                 textcoords="offset points", 
                 xytext=(0, 10),
                 ha='center', 
                 fontsize=10, 
                 color='green',
                 fontweight='bold')
    
    # Calcular estadísticas para el análisis
    pico_maximo = max(voltajes)
    pico_minimo = min(voltajes)
    promedio = np.mean(voltajes)
    
    # Encontrar los índices de los picos
    indice_maximo = voltajes.index(pico_maximo)
    indice_minimo = voltajes.index(pico_minimo)
    
    # Extraer las horas correspondientes
    hora_pico_maximo = tiempos[indice_maximo].strftime('%I:%M %p')
    hora_pico_minimo = tiempos[indice_minimo].strftime('%I:%M %p')
    
    # Agregar un recuadro con el análisis
    # Calculamos una posición en la parte inferior izquierda para no interferir con la gráfica
    x_rango = (end_time - start_time).total_seconds() / 3600  # Rango en horas
    x_pos = mdates.date2num(start_time + timedelta(hours=x_rango * 0.05))
    y_pos = 22.0  # Posición más baja para aprovechar el espacio vacío
    
    # Crear el texto del análisis con símbolos cuadrados para mejor visualización
    texto_analisis = f"ANÁLISIS DE VOLTAJE:\n\n" \
                    f"□ Pico máximo: {pico_maximo:.2f}V a las {hora_pico_maximo}\n" \
                    f"□ Pico mínimo: {pico_minimo:.2f}V a las {hora_pico_minimo}\n" \
                    f"□ Promedio: {promedio:.2f}V"
    
    # Añadir el recuadro con el análisis
    plt.annotate(texto_analisis, 
                xy=(x_pos, y_pos),
                xycoords='data',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightyellow', 
                          alpha=0.8, edgecolor='gray'),
                fontsize=10, ha='left', va='top',
                zorder=10)  # Mayor zorder para asegurar que esté por encima de otros elementos
    
    # Marcar los puntos de máximo y mínimo en la gráfica
    plt.plot(tiempos[indice_maximo], voltajes[indice_maximo], 'ro', markersize=8)  # Punto rojo para máximo
    plt.annotate("Máximo", (tiempos[indice_maximo], voltajes[indice_maximo]),
                 xytext=(10, 0), textcoords="offset points", 
                 color="red", fontweight="bold")
                 
    plt.plot(tiempos[indice_minimo], voltajes[indice_minimo], 'go', markersize=8)  # Punto verde para mínimo
    plt.annotate("Mínimo", (tiempos[indice_minimo], voltajes[indice_minimo]),
                 xytext=(10, 0), textcoords="offset points", 
                 color="green", fontweight="bold")
    
    plt.tight_layout()
    
    # Asegurar que el directorio de imágenes exista
    os.makedirs(IMG_DIR, exist_ok=True)
    
    # Guardar la gráfica en PNG con nombre específico para la ubicación
    nombre_imagen = os.path.join(IMG_DIR, f"voltage_last24hours_{ubicacion}.png")
    
    plt.savefig(nombre_imagen)
    plt.close()
    print(f"Gráfica para {ubicacion} guardada en {nombre_imagen}")
    
    # También guardamos una copia como archivo general para compatibilidad con scripts existentes
    if ubicacion == "Montecristo":  # Solo para la ubicación principal
        nombre_general = os.path.join(IMG_DIR, "voltage_last24hours.png")
        import shutil
        shutil.copy2(nombre_imagen, nombre_general)
        print(f"Copia guardada como archivo general: {nombre_general}")
    
    return True

def main():
    # Si se proporciona una ubicación específica como argumento
    if len(sys.argv) > 1:
        ubicacion = sys.argv[1]
        if ubicacion in UBICACIONES:
            generar_grafica_voltaje(ubicacion)
        else:
            print(f"Ubicación '{ubicacion}' no encontrada. Ubicaciones disponibles: {UBICACIONES}")
    else:
        # Generar gráficas para todas las ubicaciones
        for ubicacion in UBICACIONES:
            generar_grafica_voltaje(ubicacion)

if __name__ == "__main__":
    main()