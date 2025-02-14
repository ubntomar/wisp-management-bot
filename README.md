
# WhatsApp Device Control Bot

Este repositorio contiene scripts en Node.js utilizando Express y librerías como WhatsApp Web. Están diseñados para recibir órdenes desde WhatsApp y mejorar la interacción con información técnica de dispositivos MikroTik y Ubiquiti. Estos scripts se ejecutan en un VPS y están desarrollados para una empresa WISP.

## Funcionalidad

El sistema permite la interacción automatizada a través de WhatsApp, facilitando la ejecución de comandos específicos para la gestión de dispositivos de red. Los comandos son procesados por el bot y ejecutan acciones como búsqueda de clientes, ping a dispositivos y obtención de información técnica.

### Principales Características

- **Recepción de Comandos vía WhatsApp**: Los comandos son enviados desde un grupo de WhatsApp y procesados por el bot.
- **Búsqueda de Clientes**: Permite buscar información de clientes en la base de datos mediante comandos específicos.
- **Gestión de Dispositivos MikroTik y Ubiquiti**: Conexión y consulta de información técnica de dispositivos mediante SSH.
- **Ping y Estado de la Red**: Realiza pruebas de ping y verifica el estado de la VPN y las rutas de red.
- **Automatización y Respuesta**: Automatiza respuestas con la información obtenida y notifica sobre el estado de la red y dispositivos.

## Requisitos

- Node.js y npm instalados.
- Un servidor VPS con acceso a internet.
- Librerías necesarias: `whatsapp-web.js`, `express`, `mysql2`, `axios`, `os-utils`, entre otras.
- Configuración de un archivo `.env` para la conexión a la base de datos MySQL y otras credenciales.

## Instalación

1. Clona este repositorio:

   ```bash
   git clone https://github.com/ubntomar/wisp-management-bot.git
   cd wisp-management-bot
   ```

2. Instala las dependencias necesarias:

   ```bash
   npm install
   ```

3. Configura las variables de entorno en el archivo `.env` en la ruta especificada en `index.js` (`/var/www/ispexperts/login/.env`), que debe incluir credenciales de la base de datos MySQL y otras configuraciones necesarias.

4. Ejecuta el bot:

   ```bash
   node index.js
   ```

## Uso

### Comandos Disponibles

- **`soporte@red`**: Muestra el estado actual del sistema (uso de CPU y memoria).
- **`ping@<IP>`**: Realiza un ping a la IP especificada y muestra el resultado.
- **`cliente@<nombre>`**: Busca información de un cliente por nombre, apellido, dirección o cédula.
- **`ip@disponibles`**: Muestra una lista de IPs disponibles en diferentes redes.
- **`comandos@`**: Muestra la lista de comandos disponibles y su descripción.

### Cómo Funciona

1. **Inicialización**: El bot se conecta a WhatsApp y se autentica utilizando `whatsapp-web.js` con `LocalAuth`.
2. **Recepción de Mensajes**: Escucha los mensajes en el grupo especificado y procesa


### Uso de PM2 para la Gestión de Procesos

Para asegurar que los scripts `index.js` y `device_api.js` se ejecuten automáticamente y se reinicien en caso de fallo o reinicio del servidor, puedes utilizar PM2, un gestor de procesos para Node.js.

#### Instalación de PM2

Primero, instala PM2 globalmente en tu servidor:

```bash
npm install pm2@latest -g
```

#### Configuración de PM2

1. **Iniciar los scripts con PM2**:

   ```bash
   pm2 start index.js --name "wisp-bot"
   pm2 start device_api.js --name "device-api"
   ```

2. **Guardar la configuración de PM2**:

   ```bash
   pm2 save
   ```

3. **Configurar PM2 para iniciar en el arranque del sistema**:

   ```bash
   pm2 startup
   ```

   Este comando generará una línea de comando específica para tu sistema operativo. Ejecuta la línea proporcionada para completar la configuración.

#### Verificación y Gestión

- **Verificar el estado de los procesos**:

  ```bash
  pm2 status
  ```

- **Reiniciar un proceso**:

  ```bash
  pm2 restart <nombre_del_proceso>
  ```

- **Detener un proceso**:

  ```bash
  pm2 stop <nombre_del_proceso>
  ```

- **Ver logs de un proceso**:

  ```bash
  pm2 logs <nombre_del_proceso>
  ```

Con estos pasos, tus scripts `index.js` y `device_api.js` estarán gestionados por PM2, asegurando su disponibilidad continua incluso después de reinicios del servidor.

