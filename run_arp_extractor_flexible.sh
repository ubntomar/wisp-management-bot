#!/bin/bash

# Configuración por defecto
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
