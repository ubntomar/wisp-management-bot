#!/bin/bash

# Configuración del directorio de trabajo
SCRIPT_DIR="/home/omar/whatssapp/wisp-management-bot"
cd "$SCRIPT_DIR" || {
    echo "[$(date)] ERROR: No se pudo cambiar al directorio $SCRIPT_DIR" >> logs/arp_extractor.log
    exit 1
}

# Función de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$SCRIPT_DIR/logs/arp_extractor.log"
}

# Crear directorio de logs si no existe
mkdir -p logs

log "=== INICIO EXTRACCIÓN ARP ==="
log "Directorio: $SCRIPT_DIR"

# Verificar que el script Python existe
if [ ! -f "arp_extractor.py" ]; then
    log "ERROR: Script arp_extractor.py no encontrado"
    exit 1
fi

# Ejecutar con AUTO-DETECCIÓN para que use TODAS las credenciales (8 total)
log "Ejecutando script Python con auto-detección..."
timeout 300 /usr/bin/python3 arp_extractor.py 192.168.26.1 auto >> logs/arp_extractor.log 2>&1
EXIT_CODE=$?

# Verificar resultado
case $EXIT_CODE in
    0)
        log "✅ Script ejecutado exitosamente"
        ;;
    124)
        log "❌ ERROR: Timeout - Script tardó más de 5 minutos"
        ;;
    *)
        log "❌ ERROR: Script falló con código $EXIT_CODE"
        ;;
esac

log "=== FIN EXTRACCIÓN ARP ==="
log "----------------------------------------"

exit $EXIT_CODE
