#!/bin/bash

# Ir al directorio del script
cd /home/omar/whatssapp/wisp-management-bot

# Verificar que existe el archivo .env
if [ ! -f ".env" ]; then
    echo "ERROR: Archivo .env no encontrado" >> logs/arp_extractor.log
    exit 1
fi

# Cargar variables de entorno del archivo .env
# Método 1: usando export
set -a  # automatically export all variables
source .env
set +a  # turn off automatic export

# Método alternativo por si el anterior no funciona:
# eval $(grep -v '^#' .env | xargs -d '\n' -I {} echo export {})

# Configurar PATH completo para crontab
export PATH="/usr/local/bin:/usr/bin:/bin"

# Ejecutar el script Python
/usr/bin/python3 /home/omar/whatssapp/wisp-management-bot/arp_extractor.py 192.168.26.1 mikrotik >> logs/arp_extractor.log 2>&1

# Capturar código de salida
EXIT_CODE=$?

# Logging del resultado
if [ $EXIT_CODE -eq 0 ]; then
    echo "[$(date)] Script ejecutado exitosamente" >> logs/arp_extractor.log
else
    echo "[$(date)] Script falló con código $EXIT_CODE" >> logs/arp_extractor.log
fi

exit $EXIT_CODE
