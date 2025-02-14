const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const os = require('os');
const osu = require('os-utils');
const qrcode = require('qrcode-terminal');
const ping = require('ping');
const mysql = require('mysql2/promise');
require('dotenv').config();
const Redis = require('redis');
const subscriber = Redis.createClient();
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);


const axios = require('axios');

console.log('Iniciando script...');




// Configuración
const CONFIG = {
    GROUP_NAME: "Bitacora Omar",
    SUPPORT_COMMAND: "soporte@red",
    PING_COMMAND: "ping@",
    CLIENT_COMMAND: "cliente@",
    INFO_COMMAND: "info@",
    IP_COMMAND: "ip@disponibles",
    COMMANDS_INFO: "comandos@",
    CLIENT_ID: "client-one",
    DB_CONFIG: {
        host: process.env.MYSQL_SERVER,
        user: process.env.MYSQL_USER,
        password: process.env.MYSQL_PASSWORD,
        database: process.env.MYSQL_DATABASE
    },
    VOLT_COMMANDS: {
        montecristo: "volt@montecristo",
        retiro: "volt@retiro"
    },
    VOLTAGE_ENDPOINTS: {
        montecristo: "http://192.168.21.253:8013/50",
        retiro: "http://192.168.21.253:8013/50"  // Mismo endpoint para ambos
    }
};






console.log('Configuración cargada:', CONFIG);//

const client = new Client({
    authStrategy: new LocalAuth({ clientId: CONFIG.CLIENT_ID }),
    puppeteer: {
        args: ['--no-sandbox'],
    }
});

console.log('Cliente WhatsApp inicializado');

client.on('qr', (qr) => {
    console.log('Generando código QR...');
    qrcode.generate(qr, { small: true });
    console.log('Código QR generado. Por favor, escanéalo con tu teléfono.');
});

client.on('ready', () => {
    console.log('Cliente ready .. listo y conectado.');
});

client.on('authenticated', () => {
    console.log('Cliente autenticado exitosamente.');
});

client.on('auth_failure', msg => {
    console.error('Fallo en la autenticación:', msg);
});

client.on('disconnected', (reason) => {
    console.log('Cliente desconectado. Razón:', reason);
    console.log('Intentando reconexión en 5 segundos...');
    setTimeout(() => {
        console.log('Iniciando reconexión...');
        client.initialize();
    }, 5000);
});


(async () => {
    await subscriber.connect();
    console.log('Redis subscriber connected');

    await subscriber.subscribe('whatsapp_messages', async (message) => {
        console.log('Received message from Redis:', message);
        try {
            const data = JSON.parse(message);
            const { phoneNumber, message: textMessage, image } = data;

            // Asegurarse de que el cliente está listo
            if (!client.info) {
                throw new Error('Cliente de WhatsApp no está listo');
            }

            // Formatear el número de teléfono
            const formattedNumber = formatPhoneNumber(phoneNumber);
            console.log('Sending message to formatted number:', formattedNumber);
            
            // Si hay una imagen, enviarla con o sin mensaje
            if (image) {
                const media = new MessageMedia('image/png', Buffer.from(image).toString('base64'));
                await client.sendMessage(`${formattedNumber}@c.us`, media, {
                    caption: textMessage || ''
                });
                console.log('Image sent successfully');
            } 
            // Si solo hay mensaje, enviar texto
            else if (textMessage) {
                await client.sendMessage(`${formattedNumber}@c.us`, textMessage);
                console.log('Message sent successfully');
            }

            console.log(`Mensaje enviado a ${formattedNumber}`);
        } catch (error) {
            console.error('Error processing WhatsApp message:', error);
        }
    });
})();


function formatPhoneNumber(phone) {
    // Eliminar cualquier caracter que no sea número
    let cleaned = phone.replace(/\D/g, '');
    
    // Asegurarse de que tiene el formato correcto para WhatsApp
    if (cleaned.startsWith('0')) {
        cleaned = '57' + cleaned.slice(1);
    } else if (!cleaned.startsWith('57')) {
        cleaned = '57' + cleaned;
    }
    
    return cleaned;
}


client.on('message', async (msg) => {
    console.log('Mensaje recibido:', msg.body);
    try {
        const chat = await msg.getChat();
        if (chat.name === CONFIG.GROUP_NAME) {
            console.log(`Mensaje recibido en el grupo ${chat.name}: ${msg.body}`);
            if (msg.body.includes(CONFIG.SUPPORT_COMMAND)) {
                console.log('Comando de soporte detectado. Enviando estado del sistema...');
                sendSystemStatus(chat);
            } else if (msg.body.startsWith(CONFIG.PING_COMMAND)) {
                console.log('Comando de ping detectado. Procesando...');
                const ip = msg.body.split('@')[1];
                console.log('IP extraída:', ip);
                if (isValidIP(ip)) {
                    console.log('IP válida. Iniciando proceso de ping...');
                    await handlePingCommand(ip, chat);
                } else {
                    console.log('IP no válida. Enviando mensaje de error...');
                    chat.sendMessage(`La IP proporcionada (${ip}) no es válida.`);
                }
            } else if (msg.body.startsWith(CONFIG.CLIENT_COMMAND)) {
                console.log('Comando de búsqueda de cliente detectado. Procesando...');
                const searchTerm = msg.body.split('@')[1];
                console.log('Término de búsqueda:', searchTerm);
                searchClient(searchTerm, chat);
            } else if (msg.body.includes(CONFIG.IP_COMMAND)) {
                console.log('Comando de búsqueda de IPs disponibles detectado. Procesando...');
                chat.sendMessage(`Comando de búsqueda de IPs disponibles  detectado. Procesando...`)
                chat.sendMessage(`Se están buscando ips que nunca hallan pertenecido a ningún cliente en el sistema y por otro lado ips que no respondan a ping para evitar ips duplicadas`)
                await handleAvailableIPsCommand(chat);
            } else if (msg.body.includes(CONFIG.COMMANDS_INFO)) {
                console.log('Comando de información de comandos detectado. Procesando...');
                await handleCommandsInfo(chat);
            } else if (msg.body.startsWith(CONFIG.INFO_COMMAND)) {
                const ip = msg.body.split('@')[1];
                if (isValidIP(ip)) {
                    try {
                        const deviceInfo = await getDeviceInfo(ip);
                        let message = `📡 Información del dispositivo (${deviceInfo.type}):\n\n`;
                        
                        if (deviceInfo.type === 'mikrotik' || deviceInfo.type === 'ubiquiti') {
                            message += `🔗 IP: ${ip}\n`;
            
                            // Manejar la información de señal
                            if (deviceInfo.info.signalStrength && deviceInfo.info.signalStrength !== 'no such item') {
                                const signalMatch = deviceInfo.info.signalStrength.match(/-\d+/);
                                if (signalMatch) {
                                    message += `📶 Señal: ${signalMatch[0]} dBm\n`;
                                } else {
                                    message += `📶 Señal: ${deviceInfo.info.signalStrength}\n`;
                                }
                            } else {
                                message += `📶 Señal: No disponible\n`;
                            }
                            
                            // Manejar la información de velocidad
                            if (deviceInfo.info.etherRate && deviceInfo.info.etherRate !== 'no such item') {
                                if (deviceInfo.info.etherRate.includes('status: no-link')) {
                                    message += `⚠️ ALERTA: Interfaz LAN sin enlace. Posible daño en la interfaz.\n`;
                                } else {
                                    const speedMatch = deviceInfo.info.etherRate.match(/(\d+)(\w+)/);
                                    if (speedMatch) {
                                        const speed = parseInt(speedMatch[1]);
                                        const unit = speedMatch[2];
                                        message += `⚡ Velocidad: ${speed}${unit}`;
                                        if (speed === 10) {
                                            message += ` ⚠️ ALERTA: Posible problema en la interfaz Ethernet\n`;
                                        } else {
                                            message += `\n`;
                                        }
                                    } else {
                                        message += `⚡ Velocidad: No disponible\n`;
                                    }
                                }
                            } else {
                                message += `⚡ Velocidad: No disponible\n`;
                            }
            
                            // Añadir lista de direcciones ARP
                            message += `\n📋 Direcciones ARP activas:\n`;
                            if (deviceInfo.info.arpList && deviceInfo.info.arpList.length > 0) {    
                                deviceInfo.info.arpList.forEach((address, index) => {
                                    message += `   ${index + 1}. ${address}\n`;
                                });
                                // Añadir resumen si hay más de 10 IPs
                                if (deviceInfo.info.ipSummary) {
                                    message += `\n📊 Resumen de IPs por subred:\n`;
                                    deviceInfo.info.ipSummary.forEach(summary => {
                                        message += `   ${summary}\n`;
                                    });
                                }

                            } else {
                                message += `   No se encontraron direcciones ARP activas\n`;
                            }
                        
                        }
            
                        // Añadir interpretación de la señal solo si hay un valor válido
                        const signalMatch = message.match(/Señal: (-\d+)/);
                        if (signalMatch) {
                            const signalStrength = parseInt(signalMatch[1]);
                            if (!isNaN(signalStrength)) {
                                if (signalStrength > -50) message += `\n📊 Calidad de señal: Excelente 🟢`;
                                else if (signalStrength > -60) message += `\n📊 Calidad de señal: Muy buena 🟢`;
                                else if (signalStrength > -70) message += `\n📊 Calidad de señal: Buena 🟡`;
                                else if (signalStrength > -80) message += `\n📊 Calidad de señal: Regular 🟠`;
                                else message += `\n📊 Calidad de señal: Mala 🔴`;
                            }
                        }
            
                        await chat.sendMessage(message);
                    } catch (error) {
                        console.error('Error al obtener información del dispositivo:', error);
                        await chat.sendMessage(`❌ No se pudo obtener información del dispositivo: ${error.message}`);
                    }
                } else {
                    await chat.sendMessage(`❌ La IP proporcionada (${ip}) no es válida.`);
                }
            } else if (msg.body.includes(CONFIG.VOLT_COMMANDS.montecristo)) {
                console.log('Comando de voltaje Montecristo detectado. Procesando...');
                try {
                    const voltageResult = await getVoltage('montecristo');
                    if (voltageResult.success) {
                        await chat.sendMessage(`📊 Voltaje actual en Montecristo: ${voltageResult.voltage}V`);
                    } else {
                        await chat.sendMessage(`❌ Error al obtener el voltaje en Montecristo: ${voltageResult.error}`);
                    }
                } catch (error) {
                    console.error('Error procesando comando de voltaje para Montecristo:', error);
                    await chat.sendMessage('❌ Error al procesar el comando de voltaje para Montecristo');
                }
            } else if (msg.body.includes(CONFIG.VOLT_COMMANDS.retiro)) {
                console.log('Comando de voltaje Retiro detectado. Procesando...');
                try {
                    const voltageResult = await getVoltage('retiro');
                    if (voltageResult.success) {
                        await chat.sendMessage(`📊 Voltaje actual en Retiro: ${voltageResult.voltage}V`);
                    } else {
                        await chat.sendMessage(`❌ Error al obtener el voltaje en Retiro: ${voltageResult.error}`);
                    }
                } catch (error) {
                    console.error('Error procesando comando de voltaje para Retiro:', error);
                    await chat.sendMessage('❌ Error al procesar el comando de voltaje para Retiro');
                }
            }

        }
    } catch (error) {
        console.error('Error procesando el mensaje:', error);
    }
});

async function searchClient(searchTerm, chat) {
    console.log(`Buscando cliente: ${searchTerm}`);
    let connection;
    try {   
        connection = await mysql.createConnection(CONFIG.DB_CONFIG);
        
        const words = searchTerm.toLowerCase().split(' ').filter(word => word.trim() !== '');
        
        let query = `
            SELECT id, cliente, apellido, cedula, direccion, ciudad, telefono, ip, 
                   suspender, suspenderFecha, \`suspender-list-status\` AS suspender_list_status,
                   \`suspender-list-status-date\` AS suspender_list_status_date,
                   reconectPending, \`reconected-date\` AS reconected_date, pingDate
            FROM afiliados 
            WHERE activo = 1 AND eliminar = 0 
            AND (`;
        
        const conditions = [];
        const params = [];
        
        words.forEach(word => {
            conditions.push(`LOWER(CONCAT(cliente, ' ', apellido)) LIKE ?`);
            params.push(`%${word}%`);
        });
        
        query += conditions.join(' AND ') + ') LIMIT 10';

        // Imprimir la consulta SQL con los valores reales (solo para depuración)
        const sqlWithValues = query.replace(/\?/g, () => {
            const value = params.shift();
            params.unshift(value); // Volver a añadir el valor al principio del array
            return `'${value}'`;
        });
        console.log("Consulta SQL a ejecutar:", sqlWithValues);

        const [rows] = await connection.execute(query, params);
        
        if (rows.length === 0) {
            await chat.sendMessage(`🔍 No se encontraron clientes activos que coincidan con "${searchTerm}"`);
        } else {
            let message = `🔍 Se encontraron ${rows.length} cliente(s) activo(s) que coinciden con "${searchTerm}":\n\n`;
            for (const [index, client] of rows.entries()) {
                message += `👤 Cliente #${index + 1}\n`;
                message += `🆔 ID: ${client.id}\n`;
                message += `📛 Nombre: ${client.cliente} ${client.apellido}\n`;
                message += `🪪 Cédula: ${client.cedula}\n`;
                message += `📍 Dirección: ${client.direccion}, ${client.ciudad}\n`;
                message += `📞 Teléfono: ${client.telefono}\n`;
                message += `🌐 IP: ${client.ip}\n`;

                // Procesar IP del repetidor
                if (client.ip) {
                    const ipParts = client.ip.split('.');
                    if (ipParts.length === 4) {
                        const thirdOctet = ipParts[2];
                        if (thirdOctet !== '152' && thirdOctet !== '146') {
                            const repeaterSubnetGroupId = await getRepeaterSubnetGroupId(connection, thirdOctet);
                            if (repeaterSubnetGroupId) {
                                const { serverIp, apIp } = await getServerIpAndAp(connection, repeaterSubnetGroupId);
                                if (serverIp) {
                                    const pingResult = await pingIP(serverIp);
                                    message += `   📡 IP del Repetidor: ${serverIp}\n`;
                                    message += pingResult.success ? 
                                        `   ✅ Ping al repetidor: Exitoso\n` : 
                                        `   ❌ Ping al repetidor: Fallido\n`;
                                    
                                    // Verificar si la IP del repetidor termina en .1
                                    if (!serverIp.endsWith('.1')) {
                                        if (apIp) {
                                            const apPingResult = await pingIP(apIp);
                                            message += `   📡 IP del AP en el Cerro: ${apIp}\n`;
                                            message += apPingResult.success ? 
                                                `   ✅ Ping al AP en el Cerro: Exitoso\n` : 
                                                `   ❌ Ping al AP en el Cerro: Fallido\n`;
                                        } else {
                                            message += `   ⚠️ No se encontró IP del AP en el Cerro para este repetidor\n`;
                                        }
                                    }
                                    // No añadimos ningún mensaje si la IP termina en .1
                                }
                            }
                        }
                    }
                }

                // Información sobre suspensión y reconexión
                if (client.suspender_list_status === 1) {
                    const suspendDate = new Date(client.suspender_list_status_date);
                    const reconectDate = client.reconected_date ? new Date(client.reconected_date) : null;
                    
                    if (reconectDate && reconectDate >= suspendDate) {
                        const daysAgo = getDaysAgo(reconectDate);
                        message += `   🔄 Servicio reconectado ${formatDate(reconectDate)} (hace ${daysAgo} días)\n`;
                    } else {
                        message += `   🚫 Servicio suspendido desde ${formatDate(suspendDate)}\n`;
                    }
                } else if (client.suspender === 1) {
                    const suspendOrderDate = new Date(client.suspenderFecha);
                    message += `   ⚠️ Tiene orden de suspensión desde ${formatDate(suspendOrderDate)}\n`;
                }

                // Información sobre reconexión pendiente
                if (client.reconectPending === 1) {
                    message += `   🔄 Tiene una orden pendiente de reconexión\n`;
                }

                // Información sobre último ping
                if (client.ip) {
                    if (client.pingDate) {
                        const lastPingDate = new Date(client.pingDate);
                        const daysAgo = getDaysAgo(lastPingDate);
                        
                        if (daysAgo === 0) {
                            message += `   📡 Último ping exitoso a ${client.ip}: hoy\n`;
                        } else if (daysAgo === 1) {
                            message += `   📡 Último ping exitoso a ${client.ip}: ayer\n`;
                        } else {
                            message += `   📡 Último ping exitoso a ${client.ip}: hace ${daysAgo} días\n`;
                        }
                    } else {
                        console.log(`Intentando ping a ${client.ip}...`);
                        const pingResult = await pingIP(client.ip);
                        if (pingResult.success) {
                            message += `   📡 Ping exitoso a ${client.ip} (realizado ahora)\n`;
                        } else {
                            message += `   📡 No hay registro de ping exitoso a ${client.ip}\n`;
                            message += `   ❌ Intento de ping actual también fallido\n`;
                        }
                    }
                } else {
                    message += `   ❗ No hay IP registrada para este cliente\n`;
                }

                message += '\n';
            }
            await chat.sendMessage(message);
        }
    } catch (error) {
        console.error('Error en la búsqueda de clientes:', error);
        await chat.sendMessage('❌ Ocurrió un error al buscar el cliente. Por favor, intente más tarde.');
    } finally {
        if (connection) await connection.end();
    }
}
//Funcion que lleva interacción con la API REST
async function getDeviceInfo(ip) {
    console.log(`Attempting to get device info for IP: ${ip}`);
    
    async function tryDevice(deviceType) {
        console.log(`Trying ${deviceType}...`);
        try {
            const response = await axios.post('http://localhost:3124/execute-command', {
                ip,
                deviceType
            }, {
                timeout: 60000 // 60 segundos de timeout
            });
            console.log(`${deviceType} response:`, response.data);
            if (response.data.success) {
                console.log(`Successfully retrieved ${deviceType} info`);
                return { type: deviceType, info: response.data.deviceInfo };
            }
        } catch (error) {
            console.log(`Failed ${deviceType} attempt:`, error.message);
            if (error.response) {
                console.log('Error response:', error.response.data);
            } else if (error.request) {
                console.log('No response received');
            } else {
                console.log('Error details:', error.message);
            }
        }
        return null;
    }

    const mikrotikResult = await tryDevice('mikrotik');
    if (mikrotikResult) return mikrotikResult;

    const ubiquitiResult = await tryDevice('ubiquiti');
    if (ubiquitiResult) return ubiquitiResult;

    throw new Error('Unable to get device information for either Mikrotik or Ubiquiti');
}


axios.get('http://localhost:3124/test')
    .then(response => console.log('API test successful:', response.data))
    .catch(error => console.log('API test failed ,is  device_api already running ?:', error.message));




    // Función para obtener el id-repeater-subnet-group
async function getRepeaterSubnetGroupId(connection, thirdOctet) {
    console.log(`Buscando id-repeater-subnets-group para el segmento IP: ${thirdOctet}`);
    const [rows] = await connection.execute(
        'SELECT `id-repeater-subnets-group` FROM items_repeater_subnet_group WHERE `ip-segment` = ?',
        [thirdOctet]
    );
    console.log('Resultado de la consulta:', rows);
    if (rows.length > 0) {
        console.log(`id-repeater-subnets-group encontrado: ${rows[0]['id-repeater-subnets-group']}`);
        return rows[0]['id-repeater-subnets-group'];
    } else {
        console.log('No se encontró id-repeater-subnets-group');
        return null;
    }
}

// Función para obtener la server-ip e ip-ap
async function getServerIpAndAp(connection, repeaterSubnetGroupId) {
    const [rows] = await connection.execute(
        'SELECT `server-ip`, `ip-ap` FROM vpn_targets WHERE `id-repeater-subnet-group` = ?',
        [repeaterSubnetGroupId]
    );
    return rows.length > 0 ? { serverIp: rows[0]['server-ip'], apIp: rows[0]['ip-ap'] } : null;
}





// Función auxiliar para formatear fechas
function formatDate(date) {
    return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' });
}

// Función auxiliar para calcular días transcurridos
function getDaysAgo(date) {
    const now = new Date();
    const diffTime = Math.abs(now - date);
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

function sendSystemStatus(chat) {
    console.log('Obteniendo estado del sistema...');
    osu.cpuUsage((cpuPercent) => {
        const totalMem = os.totalmem() / (1024 * 1024);
        const freeMem = os.freemem() / (1024 * 1024);
        const usedMem = totalMem - freeMem;
        console.log('Datos del sistema obtenidos:', { cpuPercent, totalMem, freeMem, usedMem });
        const statusMessage = `
            Uso del Sistema:
            - CPU: ${(cpuPercent * 100).toFixed(2)}%
            - Memoria Usada: ${usedMem.toFixed(2)} MB / ${totalMem.toFixed(2)} MB
            - Memoria Libre: ${freeMem.toFixed(2)} MB
                    `;
        console.log('Enviando mensaje de estado del sistema...');
        chat.sendMessage(statusMessage)
            .then((msg) => {
                console.log('Estado del sistema enviado al grupo Soportes', msg);
            })
            .catch(error => {
                console.error('Error enviando estado del sistema:', error);
                // Intenta reenviar el mensaje
                return chat.sendMessage('Error al enviar el estado del sistema. Por favor, intente de nuevo.');
            });
    });
}

function isValidIP(ip) {
    console.log('Validando IP:', ip);
    const ipPattern = /^(\d{1,3}\.){3}\d{1,3}$/;
    if (!ipPattern.test(ip)) {
        console.log('IP no válida: no coincide con el patrón');
        return false;
    }
    const isValid = ip.split('.').every(segment => parseInt(segment) >= 0 && parseInt(segment) <= 255);
    console.log('Resultado de validación de IP:', isValid);
    return isValid;
}

// Función para realizar ping a una IP
async function pingIP(ip) {
    try {
        const { stdout, stderr } = await execPromise(`ping -c 4 ${ip}`);
        return { success: !stderr, output: stdout };
    } catch (error) {
        console.error(`Error al hacer ping a ${ip}:`, error);
        return { success: false, output: error.message };
    }
}


// Función principal para manejar el comando ping@
async function handlePingCommand(ip, chat) {
    console.log(`Iniciando verificaciones para ping a ${ip}...`);

    let message = "Estado de la conexión:\n";

    // Verificar VPN
    const vpnStatus = await checkVPNPeer();
    message += vpnStatus ? "✅ Acceso VPN: OK\n" : "❌ Acceso VPN: No disponible\n";

    // Verificar rutas
    const routesStatus = await checkRoutes();
    message += routesStatus ? "✅ Rutas de red: OK\n" : "❌ Rutas de red: Insuficientes\n";

    // Si ambas verificaciones son exitosas, proceder con el ping
    if (vpnStatus && routesStatus) {
        message += "\nRealizando ping...\n";
        const pingResult = await pingIP(ip);
        if (pingResult.success) {
            message += `✅ Ping exitoso a ${ip}\n`;
            message += pingResult.output.split('\n').slice(-2).join('\n'); // Mostrar resumen del ping
        } else {
            message += `❌ No se pudo hacer ping a ${ip}\n`;
            message += "Razón: No hay respuesta del host\n";
        }
    } else {
        message += "\n❌ No se puede realizar el ping debido a problemas de conexión.";
    }

    await chat.sendMessage(message);
}


// Función para verificar el ping al peer VPN
async function checkVPNPeer() {
    try {
        const { stdout, stderr } = await execPromise('ping -c 4 10.0.11.10');
        return !stderr && stdout.includes('4 packets transmitted, 4 received');
    } catch (error) {
        console.error('Error al hacer ping al peer VPN:', error);
        return false;
    }
}

// Función para verificar las rutas
async function checkRoutes() {
    try {
        const { stdout, stderr } = await execPromise('ip r');
        const routeCount = stdout.split('\n').filter(line => line.trim()).length;
        return !stderr && routeCount >= 10;
    } catch (error) {
        console.error('Error al verificar rutas:', error);
        return false;
    }
}

async function getAvailableIPs(network, existingIPs) {
    const baseIP = network.split('/')[0].split('.').slice(0, 3).join('.');
    let availableIPs = [];

    for (let i = 2; i <= 254; i++) {
        const ip = `${baseIP}.${i}`;
        if (!existingIPs.includes(ip)) {
            const pingResult = await pingIP(ip);
            if (!pingResult.success) {
                availableIPs.push(ip);
                if (availableIPs.length >= 3) break;
            }
        }
    }

    return availableIPs;
}

// Función para obtener IPs existentes de la base de datos
async function getExistingIPs(connection) {
    const [rows] = await connection.execute('SELECT DISTINCT ip FROM afiliados WHERE ip IS NOT NULL AND ip != ""');
    return rows.map(row => row.ip);
}

// Función principal para manejar el comando ip@disponibles
async function handleAvailableIPsCommand(chat) {
    console.log('Iniciando búsqueda de IPs disponibles...');

    let message = "Estado de la conexión:\n";

    // Verificar VPN y rutas
    const vpnStatus = await checkVPNPeer();
    const routesStatus = await checkRoutes();

    message += vpnStatus ? "✅ Acceso VPN: OK\n" : "❌ Acceso VPN: No disponible\n";
    message += routesStatus ? "✅ Rutas de red: OK\n\n" : "❌ Rutas de red: Insuficientes\n\n";

    if (!vpnStatus || !routesStatus) {
        message += "❌ No se pueden buscar IPs disponibles debido a problemas de conexión.";
        await chat.sendMessage(message);
        return;
    }

    let connection;
    try {
        connection = await mysql.createConnection(CONFIG.DB_CONFIG);
        const existingIPs = await getExistingIPs(connection);

        const networks = [
            { name: "Red Orlando", range: "192.168.27.0/24" },
            { name: "Red Montecristo", range: "192.168.16.0/24" },
            { name: "Red Retiro", range: "192.168.30.0/24" }
        ];

        for (const network of networks) {
            message += `${network.name}:\n`;
            const availableIPs = await getAvailableIPs(network.range, existingIPs);
            if (availableIPs.length > 0) {
                availableIPs.forEach(ip => {
                    message += `  - ${ip}\n`;
                });
            } else {
                message += "  No se encontraron IPs disponibles\n";
            }
            message += "\n";
        }

        await chat.sendMessage(message);
    } catch (error) {
        console.error('Error al buscar IPs disponibles:', error);
        await chat.sendMessage('Ocurrió un error al buscar IPs disponibles. Por favor, intente más tarde.');
    } finally {
        if (connection) await connection.end();
    }
}

async function handleCommandsInfo(chat) {
    const commandsInfo = `
Comandos disponibles:

1. ${CONFIG.SUPPORT_COMMAND}
   Ejemplo: soporte@red
   Descripción: Muestra el estado actual del sistema (uso de CPU y memoria).

2. ${CONFIG.PING_COMMAND}
   Ejemplo: ping@192.168.1.1
   Descripción: Realiza un ping a la IP especificada y muestra el resultado.

3. ${CONFIG.CLIENT_COMMAND}
   Ejemplo: cliente@Juan Pérez
   Descripción: Busca información de un cliente por nombre, apellido, dirección o cédula.

4. ${CONFIG.IP_COMMAND}
   Ejemplo: ip@disponibles
   Descripción: Muestra una lista de IPs disponibles en diferentes redes.

5. ${CONFIG.COMMANDS_INFO}
   Ejemplo: comandos@
   Descripción: Muestra esta lista de comandos disponibles.

6. ${CONFIG.VOLT_COMMANDS.montecristo}
   Ejemplo: volt@montecristo
   Descripción: Muestra el voltaje actual en la estación Montecristo.

7. ${CONFIG.VOLT_COMMANDS.retiro}
   Ejemplo: volt@retiro
   Descripción: Muestra el voltaje actual en la estación Retiro.   

Recuerda que todos estos comandos deben ser utilizados dentro del grupo "${CONFIG.GROUP_NAME}".
    `;

    await chat.sendMessage(commandsInfo);
}


async function getVoltage(location) {
    try {
        const endpoint = CONFIG.VOLTAGE_ENDPOINTS[location];
        if (!endpoint) {
            return {
                success: false,
                error: 'Ubicación no válida'
            };
        }

        const response = await axios.get(endpoint);
        const data = response.data;
        
        if (data && data.data && data.data.sensor1) {
            return {
                success: true,
                voltage: data.data.sensor1
            };
        } else {
            return {
                success: false,
                error: 'No se pudo obtener el voltaje'
            };
        }
    } catch (error) {
        console.error(`Error al obtener el voltaje de ${location}:`, error);
        return {
            success: false,
            error: error.message
        };
    }
}



console.log('Iniciando cliente WhatsApp...');
client.initialize().catch(err => console.error('Error al inicializar el cliente:', err));

process.on('unhandledRejection', (reason, promise) => {
    console.log('Rechazo no manejado en:', promise, 'razón:', reason);
});

process.on('uncaughtException', (error) => {
    console.error('Excepción no capturada:', error);
    console.log('El script continuará ejecutándose...');
});

setInterval(() => {
    console.log('Estado del cliente:', client.info);
    if (client.info === undefined) {
        console.log('Reiniciando cliente WhatsApp...');
        client.initialize().catch(err => console.error('Error al reinicializar el cliente:', err));
    }else
    {
        console.log('Cliente WhatsApp en linea...');
    }
  }, 60000); // Comprueba cada minuto

console.log('Script completamente cargado y en ejecución.');
