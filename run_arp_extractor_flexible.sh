#!/bin/bash


printf "Iniciando el script run_arp_extractor_flexible.sh\n"
printf "Este script debe se conecta a un endpoint de WhatsApp para enviar mensajes.\n"
printf "Asegúrate de que el VPS 45.61.59.204 asterisk  esté en funcionamiento y accesible.\n"
printf "OJO (omar@botandusa:~/wisp-management-bot) Pm2 list : lista und enpoint pero del 316295!!! NO útil para este proyecyo!\n"


echo "--------------------------------------------------------------------------------------------------------------------" >> logs/arp_extractor.log
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Iniciando run_arp_extractor_flexible.sh" >> logs/arp_extractor.log
echo "Asegúrate de que el VPS 45.61.59.204  ssh asterisk  esté en funcionamiento y accesible.\n" >> logs/arp_extractor.log
echo "Pm2 list lista und enpoint pero del 316295!!! NO útil para este proyecyo!" >> logs/arp_extractor.log


printf "Comprobando, timeout 5 nc -zv 45.61.59.204 8050  ,conexión al VPS 45.61.59.204 (asterisk)  en el puerto 8050...\n"
timeout 5 nc -zv 45.61.59.204 8050
if [ $? -ne 0 ]; then
    printf "Error: No se pudo conectar al VPS 45.61.59.204 en el puerto 8050.\n"
    printf "Saliendo del script.\n"
    echo "Error: No se pudo conectar al VPS 45.61.59.204 (ssh asterisk) en el puerto 8050." >> logs/arp_extractor.log
    exit 1
fi

# Configuración por defecto--
DEFAULT_IP="192.168.26.1"
DEFAULT_TYPE="auto"

# Parámetros del script
IP="${1:-$DEFAULT_IP}"
TYPE="${2:-$DEFAULT_TYPE}"
WHATSAPP_TARGET="$3"

# Ir al directorio correcto
cd /home/omar/whatssapp/wisp-management-bot

# Crear logs si no existe
mkdir -p logs

# Construir comando base
CMD="/usr/bin/python3 arp_extractor.py $IP $TYPE"

# Agregar target de WhatsApp si se especifica
if [ -n "$WHATSAPP_TARGET" ]; then
    CMD="$CMD --whatsapp-target $WHATSAPP_TARGET"
fi

# Logging del inicio
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Ejecutando: $CMD" >> logs/arp_extractor.log

# Ejecutar comando
$CMD >> logs/arp_extractor.log 2>&1
EXIT_CODE=$?

# Logging del resultado
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Script terminado con código $EXIT_CODE" >> logs/arp_extractor.log
echo "----------------------------------------" >> logs/arp_extractor.log

exit $EXIT_CODE
