# Sistema de Gestión WISP via WhatsApp

Bot automatizado integral para gestión de infraestructura de red en empresas WISP (Wireless Internet Service Provider). Combina Node.js, Python y Redis para proporcionar gestión completa de dispositivos de red, monitoreo de clientes y diagnósticos de red a través de WhatsApp.

## 🏗️ Arquitectura del Sistema

### Componentes Principales

#### 1. **Bot Principal de WhatsApp** (`index.js`)
- **Cliente WhatsApp Web**: Autenticación persistente con `whatsapp-web.js`
- **Procesamiento de Comandos**: 8 comandos específicos para el grupo "Soportes"
- **Integración Redis**: Suscriptor para mensajes desde servicios externos
- **Base de Datos MySQL**: Consultas de clientes y configuraciones
- **Auto-reconexión**: Monitoreo continuo y reinicio automático

#### 2. **API de Dispositivos** (`device_api.js`)
- **Servidor Express**: API REST en puerto 3124
- **SSH Multiconexión**: 8 credenciales (4 MikroTik + 4 Ubiquiti)
- **Endpoint Mensajería**: `/send-message` con soporte de imágenes
- **Extracción de Datos**: Comandos específicos por tipo de dispositivo
- **Publicador Redis**: Comunicación con bot principal

#### 3. **Sistema de Monitoreo de Voltaje**
- **Recolector** (`sensorDataToDb.py`): Datos de sensores vía HTTP API
- **Generador de Gráficas** (`image_generator.py`): Visualizaciones con matplotlib
- **Distribuidor** (`whatsapp_sender.py`): Envío automático de reportes visuales
- **Almacenamiento Redis**: Series temporales para análisis histórico

#### 4. **Herramientas Independientes**
- **Extractor ARP** (`arp_extractor.py`): Script independiente para análisis de ARP
- **Utilidades de Consulta** (`query.py`, `populate.py`): Herramientas de datos
- **Pruebas SSH** (`ssh_test.js`): Diagnóstico de conexiones

## 🔧 Funcionalidades Principales

### Bot de WhatsApp - Comandos Disponibles

| Comando | Ejemplo | Descripción |
|---------|---------|-------------|
| `soporte@red` | `soporte@red` | Estado del sistema (CPU, memoria) |
| `ping@<IP>` | `ping@192.168.1.1` | Ping con verificación VPN/rutas |
| `cliente@<busqueda>` | `cliente@Juan Pérez` | Búsqueda de clientes por nombre/IP/cédula |
| `info@<IP>` | `info@192.168.1.1` | Información técnica de dispositivos |
| `ip@disponibles` | `ip@disponibles` | IPs disponibles en redes configuradas |
| `volt@montecristo` | `volt@montecristo` | Voltaje actual en Montecristo |
| `volt@retiro` | `volt@retiro` | Voltaje actual en Retiro |
| `comandos@` | `comandos@` | Lista de comandos disponibles |

### Información de Dispositivos (MikroTik/Ubiquiti)
- 📶 **Señal WiFi**: Intensidad y calidad con interpretación colorizada
- ⚡ **Velocidad de Interfaces**: Detección de problemas de conectividad
- 📋 **Tablas ARP**: Direcciones IP activas con resumen por subred
- 🔗 **Estado de Enlaces**: Diagnóstico de interfaces LAN/WAN
- 📊 **Análisis de Red**: Distribución de clientes por subred

### Gestión de Clientes
- 🔍 **Búsqueda Avanzada**: Por nombre, apellido, dirección, cédula o IP
- 📡 **Estado de Conectividad**: Ping automático con historial
- 🔄 **Estado de Servicio**: Suspensiones, reconexiones y fechas
- 🌐 **Información de Repetidores**: IPs de repetidores y APs
- 📞 **Datos de Contacto**: Información completa del cliente

### Monitoreo de Voltaje
- 📊 **Gráficas en Tiempo Real**: Últimas 24 horas por ubicación
- 🔋 **Alertas Automáticas**: Notificaciones de variaciones críticas
- 📈 **Análisis Histórico**: Almacenamiento en Redis con timestamps
- 🖼️ **Reportes Visuales**: Envío automático de gráficas por WhatsApp

## 🛠️ Requisitos Técnicos

### Software Base
- **Node.js** v14+ con npm
- **Python** 3.8+ con pip  
- **Redis Server** 6.0+
- **MySQL** 8.0+
- **PM2** (recomendado para producción)

### Dependencias Node.js
```json
{
  "whatsapp-web.js": "^1.26.0",
  "express": "^4.19.2", 
  "mysql2": "^3.11.0",
  "redis": "^4.7.0",
  "node-ssh": "^13.2.0",
  "axios": "^1.7.7",
  "os-utils": "^0.0.14",
  "ping": "^0.4.4",
  "multer": "^1.4.5-lts.1",
  "qrcode-terminal": "^0.12.0",
  "dotenv": "^16.4.5"
}
```

### Dependencias Python
```bash
pip install requests redis matplotlib paramiko python-dotenv
```

## 📥 Instalación

### 1. Clonar y Preparar
```bash
git clone https://github.com/ubntomar/wisp-management-bot.git
cd wisp-management-bot
npm install
pip install requests redis matplotlib paramiko python-dotenv
```

### 2. Configurar Variables de Entorno
Crear archivo `.env`:

```env
# Base de Datos MySQL
MYSQL_SERVER=localhost
MYSQL_USER=usuario_db
MYSQL_PASSWORD=password_db
MYSQL_DATABASE=wisp_database

# SSH Credentials - MikroTik (4 sets)
ADMIN_PASS=mikrotik_pass1
ADMIN_PASS2=mikrotik_pass2
AGINGENIERIA_PASS=mikrotik_pass3
AGINGENIERIA_PASS2=mikrotik_pass4

# SSH Credentials - Ubiquiti (4 sets)
UBNT_USER=ubiquiti_user
UBNT_PASS=ubiquiti_pass1
UBNT_PASS2=ubiquiti_pass2
UBNT_PASS3=ubiquiti_pass3
UBNT_PASS4=ubiquiti_pass4

# WhatsApp Configuration
PHONE_GROUP_SOPORTES=grupo_id_soportes

# API Settings
API_PORT=3124

# ARP Extractor (Opcional - para uso independiente)
WHATSAPP_API_ENDPOINT=http://localhost:3124/send-message
WHATSAPP_TARGET_NUMBER=573161234567
```

### 3. Inicializar Servicios
```bash
# Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# MySQL (crear esquema de base de datos)
mysql -u root -p < database_schema.sql

# Crear directorios necesarios
mkdir -p logs img
```

## 🚀 Ejecución

### Desarrollo
```bash
# Terminal 1: API de dispositivos
node device_api.js

# Terminal 2: Bot principal
node index.js
```

### Producción con PM2
```bash
# Instalar PM2
npm install pm2@latest -g

# Iniciar servicios
pm2 start device_api.js --name "device-api"
pm2 start index.js --name "wisp-bot"

# Configurar inicio automático
pm2 save
pm2 startup

# Monitoreo
pm2 status
pm2 logs wisp-bot
pm2 logs device-api
```

## 📊 Uso del Sistema

### Gestión de Clientes
```
# Búsqueda por nombre
cliente@Juan Pérez

# Búsqueda por IP
cliente@192.168.1.100

# Búsqueda por cédula
cliente@12345678
```
**Respuesta incluye**: Datos personales, IP asignada, estado de servicio, último ping, información de repetidores.

### Diagnóstico de Red
```
# Ping con verificación previa
ping@192.168.1.1

# Información técnica completa
info@192.168.1.1

# IPs disponibles
ip@disponibles
```

### Monitoreo de Voltaje
```
# Lecturas actuales
volt@montecristo
volt@retiro

# Estado del sistema
soporte@red
```

### Extractor ARP (Independiente)
```bash
# Uso básico
python arp_extractor.py 192.168.1.1

# Especificar dispositivo
python arp_extractor.py 192.168.1.254 mikrotik

# Sin WhatsApp
python arp_extractor.py 192.168.1.1 --no-whatsapp

# Target específico
python arp_extractor.py 192.168.1.1 --whatsapp-target 573161234567
```

## 🔍 Características Técnicas Avanzadas

### Manejo de Credenciales SSH
- **8 conjuntos de credenciales**: 4 MikroTik + 4 Ubiquiti
- **Failover automático**: Prueba credenciales secuencialmente
- **Timeout configurable**: 20 segundos por intento
- **Algoritmos legacy**: Compatibilidad con dispositivos antiguos

### Sistema de Diagnóstico de Red
- **Verificación VPN**: Ping a peer VPN antes de operaciones
- **Validación de Rutas**: Conteo de rutas activas disponibles
- **Ping inteligente**: Solo ejecuta si VPN y rutas están OK
- **Interpretación de señal**: Clasificación por calidad (Excelente/Buena/Regular/Mala)

### Gestión de Datos
- **Redis para Mensajería**: Comunicación asíncrona entre componentes
- **MySQL para Clientes**: Base de datos principal con relaciones complejas
- **Caché en Redis**: Datos de voltaje con timestamps para análisis temporal
- **Archivos de log**: Rotación automática de logs por componente

### Redes Monitoreadas
- **Red Orlando**: 192.168.27.0/24
- **Red Montecristo**: 192.168.16.0/24
- **Red Retiro**: 192.168.30.0/24

## 🔧 Tareas Automatizadas

### Cron Jobs Recomendados
```bash
# Editar crontab
crontab -e

# Recolección de voltaje cada 30 minutos
*/30 * * * * /usr/bin/python3 /ruta/proyecto/sensorDataToDb.py >> /ruta/proyecto/logs/voltage.log 2>&1

# Reporte diario de voltaje 8:00 AM
0 8 * * * /usr/bin/python3 /ruta/proyecto/whatsapp_sender.py >> /ruta/proyecto/logs/daily_reports.log 2>&1

# Limpieza de logs semanal
0 2 * * 1 find /ruta/proyecto/logs -name "*.log" -mtime +7 -delete

# Backup de imágenes mensual
0 3 1 * * tar -czf /backup/img-$(date +\%Y\%m).tar.gz /ruta/proyecto/img/
```

## 📁 Estructura del Proyecto

```
wisp-management-bot/
├── 🤖 Componentes Principales
│   ├── index.js                    # Bot principal WhatsApp
│   ├── device_api.js              # API REST para dispositivos
│   └── eventEmitter.js            # Gestor de eventos
│
├── 🐍 Scripts Python
│   ├── arp_extractor.py           # Extractor ARP independiente
│   ├── whatsapp_sender.py         # Envío de mensajes con imágenes
│   ├── sensorDataToDb.py          # Recolector datos voltaje
│   ├── image_generator.py         # Generador de gráficas
│   ├── query.py                   # Consultas Redis
│   └── populate.py                # Datos de prueba
│
├── 🔧 Utilidades
│   ├── ssh_test.js                # Pruebas de conexión SSH
│   └── whatsapp_diagnostic.sh     # Diagnósticos WhatsApp
│
├── 📊 Datos y Logs
│   ├── img/                       # Gráficas generadas
│   │   ├── voltage_last24hours_Montecristo.png
│   │   ├── voltage_last24hours_Retiro.png
│   │   └── voltage_last24hours.png
│   ├── logs/                      # Archivos de registro
│   │   ├── arp_extractor.log
│   │   └── debug.log
│   └── telefonos.txt              # Números de prueba
│
├── ⚙️ Configuración
│   ├── package.json               # Dependencias Node.js
│   ├── .env                       # Variables de entorno
│   └── .gitignore                 # Archivos ignorados
│
└── 🗂️ Sistema
    ├── .wwebjs_auth/              # Autenticación WhatsApp
    ├── .wwebjs_cache/             # Cache WhatsApp
    └── node_modules/              # Módulos Node.js
```

## 🚨 Monitoreo y Logs

### Ubicación de Logs
- **Bot WhatsApp**: Console output + PM2 logs
- **API Dispositivos**: Console output + PM2 logs  
- **Extractor ARP**: `/logs/arp_extractor.log`
- **Sistema General**: `/logs/debug.log`

### Comandos de Monitoreo
```bash
# Logs en tiempo real
pm2 logs wisp-bot --lines 50
pm2 logs device-api --lines 50

# Estado de procesos
pm2 status
pm2 monit

# Logs específicos
tail -f logs/arp_extractor.log
tail -f logs/debug.log
```

### Verificaciones de Estado Automáticas
- ✅ Cliente WhatsApp conectado
- ✅ Redis publisher/subscriber activos
- ✅ Conexión MySQL disponible
- ✅ API REST respondiendo
- ✅ VPN peer alcanzable
- ✅ Rutas de red suficientes

## 🔧 Solución de Problemas

### Problemas Comunes

#### WhatsApp Bot No Responde
```bash
# Verificar estado PM2
pm2 status

# Revisar logs
pm2 logs wisp-bot

# Reiniciar si es necesario
pm2 restart wisp-bot

# Regenerar autenticación
rm -rf .wwebjs_auth .wwebjs_cache
pm2 restart wisp-bot
```

#### Fallas de Conexión SSH
```bash
# Probar conexión manual
node ssh_test.js

# Verificar credenciales en .env
cat .env | grep -E "(ADMIN_PASS|UBNT_)"

# Verificar conectividad de red
ping 192.168.1.1
```

#### Problemas con Redis
```bash
# Estado del servicio
sudo systemctl status redis-server

# Conectividad
redis-cli ping

# Logs de Redis
sudo journalctl -u redis-server -f
```

#### Errores de Base de Datos
```bash
# Conexión MySQL
mysql -u $MYSQL_USER -p$MYSQL_PASSWORD -h $MYSQL_SERVER

# Verificar tablas
SHOW TABLES;
DESCRIBE afiliados;
```

### Debug Mode

#### Activar logs detallados
```javascript
// En index.js o device_api.js
const DEBUG = true;
if (DEBUG) console.log('Debug info:', data);
```

#### Python logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🛡️ Seguridad y Mejores Prácticas

### Variables de Entorno
- ✅ Todas las credenciales en `.env`
- ✅ Archivo `.env` en `.gitignore`
- ✅ Permisos restrictivos: `chmod 600 .env`

### SSH
- ✅ Credenciales múltiples para redundancia
- ✅ Timeouts configurados
- ✅ Verificación de host deshabilitada (redes internas)

### WhatsApp
- ✅ Autenticación persistente local
- ✅ Validación de grupos específicos
- ✅ Rate limiting implícito

## 📈 Escalabilidad

### Arquitectura Distribuida
- **Extractor ARP**: Puede ejecutarse en VPS separado
- **Sistema de Voltaje**: Independiente con API propia
- **Redis**: Permite múltiples workers
- **API REST**: Escalable horizontalmente

### Configuración Multi-VPS
```env
# VPS Principal
WHATSAPP_API_ENDPOINT=http://localhost:3124/send-message

# VPS Secundario (solo ARP)
WHATSAPP_API_ENDPOINT=http://IP_VPS_PRINCIPAL:3124/send-message
```

## 🔄 Actualizaciones y Mantenimiento

### Backup Recomendado
```bash
# Script de backup diario
#!/bin/bash
BACKUP_DIR="/backup/wisp-bot-$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Configuración
cp .env $BACKUP_DIR/
cp package.json $BACKUP_DIR/

# Logs importantes
cp -r logs/ $BACKUP_DIR/

# Imágenes recientes
find img/ -mtime -7 -type f -exec cp {} $BACKUP_DIR/ \;

# Compresión
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR/
rm -rf $BACKUP_DIR/
```

### Actualizaciones
```bash
# Detener servicios
pm2 stop all

# Actualizar dependencias
npm update
pip install --upgrade requests redis matplotlib paramiko

# Reiniciar servicios
pm2 start all
```

## 📞 Soporte y Contacto

### Para Soporte Técnico
1. Revisar logs del sistema
2. Verificar estado de servicios con PM2
3. Consultar documentación de APIs
4. Contactar al equipo de desarrollo

### Información del Sistema
- **Versión**: 2.0.0
- **Última actualización**: 25 Julio 2025
- **Compatibilidad**: Node.js 14+, Python 3.8+, Redis 6.0+, MySQL 8.0+
- **Licencia**: Uso interno empresa WISP

---

**Desarrollado para gestión integral de infraestructura WISP con automatización completa via WhatsApp**
