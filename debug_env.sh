#!/bin/bash
cd /home/omar/whatssapp/wisp-management-bot

echo "=== DEBUG ENVIRONMENT ===" >> logs/debug.log
echo "Date: $(date)" >> logs/debug.log
echo "Working directory: $(pwd)" >> logs/debug.log
echo "PATH: $PATH" >> logs/debug.log
echo ".env file exists: $([ -f .env ] && echo YES || echo NO)" >> logs/debug.log

# Cargar .env
set -a
source .env 2>/dev/null
set +a

echo "ADMIN_PASS set: ${ADMIN_PASS:+YES}" >> logs/debug.log
echo "WHATSAPP_TARGET_NUMBER set: ${WHATSAPP_TARGET_NUMBER:+YES}" >> logs/debug.log
echo "=========================" >> logs/debug.log
