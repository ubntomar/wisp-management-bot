#!/bin/bash

# Configurar directorio
SCRIPT_DIR="/home/omar/whatssapp/wisp-management-bot"
cd "$SCRIPT_DIR"

# Función para logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$SCRIPT_DIR/logs/arp_extractor.log"
}

# Verificar archivo .env
if [ ! -f ".env" ]; then
    log "ERROR: Archivo .env no encontrado"
    exit 1
fi

# Cargar variables específicamente (método más directo)
export ADMIN_PASS=$(grep '^ADMIN_PASS=' .env | cut -d '=' -f2-)
export ADMIN_PASS2=$(grep '^ADMIN_PASS2=' .env | cut -d '=' -f2-)
export AGINGENIERIA_PASS=$(grep '^AGINGENIERIA_PASS=' .env | cut -d '=' -f2-)
export AGINGENIERIA_PASS2=$(grep '^AGINGENIERIA_PASS2=' .env | cut -d '=' -f2-)
export UBNT_USER=$(grep '^UBNT_USER=' .env | cut -d '=' -f2-)
export UBNT_PASS=$(grep '^UBNT_PASS=' .env | cut -d '=' -f2-)
export UBNT_PASS2=$(grep '^UBNT_PASS2=' .env | cut -d '=' -f2-)
export UBNT_PASS3=$(grep '^UBNT_PASS3=' .env | cut -d '=' -f2-)
export UBNT_PASS4=$(grep '^UBNT_PASS4=' .env | cut -d '=' -f2-)
export WHATSAPP_API_ENDPOINT=$(grep '^WHATSAPP_API_ENDPOINT=' .env | cut -d '=' -f2-)
export WHATSAPP_TARGET_NUMBER=$(grep '^WHATSAPP_TARGET_NUMBER=' .env | cut -d '=' -f2-)

# Verificar que las variables se cargaron
log "Variables cargadas - ADMIN_PASS: ${ADMIN_PASS:+SET} WHATSAPP_TARGET: ${WHATSAPP_TARGET_NUMBER:+SET}"

# Configurar PATH
export PATH="/usr/local/bin:/usr/bin:/bin"

# Ejecutar script
log "Iniciando script Python..."
/usr/bin/python3 "$SCRIPT_DIR/arp_extractor.py" 192.168.26.1 mikrotik >> "$SCRIPT_DIR/logs/arp_extractor.log" 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    log "Script completado exitosamente"
else
    log "ERROR: Script falló con código $EXIT_CODE"
fi

exit $EXIT_CODE
