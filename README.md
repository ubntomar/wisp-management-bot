
# WhatsApp Device Control Bot

Este repositorio contiene una serie de scripts en Node.js utilizando Express y librerías como WhatsApp Web, diseñados para recibir órdenes y comandos desde WhatsApp y mejorar la búsqueda e interacción con información técnica de dispositivos MikroTik y Ubiquiti. Estos scripts se ejecutan en un VPS y están desarrollados para una empresa WISP.

## Funcionalidad

El sistema permite la interacción automatizada a través de WhatsApp, facilitando la ejecución de comandos específicos que ayudan en la gestión de dispositivos de red. Los comandos son procesados por el bot y ejecutan acciones como búsqueda de clientes, ping a dispositivos, y obtención de información técnica.

### Principales Características:

- **Recepción de Comandos vía WhatsApp**: Los comandos son enviados desde un grupo de WhatsApp y procesados por el bot.
- **Búsqueda de Clientes**: Permite buscar información de clientes en la base de datos mediante comandos específicos.
- **Gestión de Dispositivos MikroTik y Ubiquiti**: Conexión y consulta de información técnica de dispositivos mediante SSH.
- **Ping y Estado de la Red**: Realiza pruebas de ping y verifica el estado de la VPN y las rutas de red.
- **Automatización y Respuesta**: Automatiza respuestas con la información obtenida y notifica sobre el estado de la red y dispositivos.

## Requisitos

- Node.js y npm instalados.
- Un servidor VPS con acceso a internet.
- Librerías necesarias: \`whatsapp-web.js\`, \`express\`, \`mysql2\`, \`axios\`, \`os-utils\`, entre otras.
- Configuración de un archivo \`.env\` para la conexión a la base de datos MySQL y otras credenciales.

## Instalación

1. Clona este repositorio:

   \`\`\`bash
   git clone https://github.com/ubntomar/wisp-management-bot.git
   cd wisp-management-bot
   \`\`\`

2. Instala las dependencias necesarias:

   \`\`\`bash
   npm install
   \`\`\`

3. Configura las variables de entorno en el archivo \`.env\` en la ruta especificada en \`index.js\` (\`/var/www/ispexperts/login/.env\`), que debe incluir credenciales de la base de datos MySQL y otras configuraciones necesarias.

4. Ejecuta el bot:

   \`\`\`bash
   node index.js
   \`\`\`

## Uso

### Comandos Disponibles

- **\`soporte@red\`**: Muestra el estado actual del sistema (uso de CPU y memoria).
- **\`ping@<IP>\`**: Realiza un ping a la IP especificada y muestra el resultado.
- **\`cliente@<nombre>\`**: Busca información de un cliente por nombre, apellido, dirección o cédula.
- **\`ip@disponibles\`**: Muestra una lista de IPs disponibles en diferentes redes.
- **\`comandos@\`**: Muestra la lista de comandos disponibles y su descripción.

### Cómo Funciona

1. **Inicialización**: El bot se conecta a WhatsApp y se autentica utilizando \`whatsapp-web.js\` con \`LocalAuth\`.
2. **Recepción de Mensajes**: Escucha los mensajes en el grupo especificado y procesa los comandos según su contenido.
3. **Ejecución de Comandos**: Cada comando dispara una función específica que interactúa con la base de datos MySQL, APIs externas o dispositivos de red.
4. **Respuesta Automática**: Envía los resultados de los comandos de vuelta al grupo de WhatsApp.

### Estructura del Proyecto

- \`index.js\`: Script principal que inicializa el cliente de WhatsApp y gestiona la recepción y ejecución de comandos.
- \`device_api.js\`: API REST que permite la ejecución de comandos en dispositivos MikroTik y Ubiquiti a través de SSH.
- \`.env\`: Archivo de configuración de variables de entorno (no incluido en el repositorio por seguridad).

## Contribuciones

Las contribuciones son bienvenidas. Puedes abrir issues para reportar problemas o enviar pull requests con mejoras.

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo \`LICENSE\` para más detalles.

## Contacto

Si tienes preguntas o necesitas soporte adicional, por favor, contacta a [tu_correo@ejemplo.com](mailto:tu_correo@ejemplo.com).

---

¡Gracias por usar WhatsApp Device Control Bot! Esperamos que mejore tu experiencia en la gestión de redes WISP.