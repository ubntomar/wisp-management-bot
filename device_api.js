const express = require('express');
const { NodeSSH } = require('node-ssh');
const dotenv = require('dotenv');

dotenv.config({ path: '/var/www/ispexperts/login/.env' });

const app = express();
app.use(express.json());

const MIKROTIK_CREDENTIALS = [
    { username: 'admin', password: 'admin' },
    { username: 'admin', password: 'agwist2017' },
    { username: 'agingenieria', password: 'admin' },
    { username: 'agingenieria', password: 'agwist2017' }
];

const UBIQUITI_CREDENTIALS = [
    { username: 'ubnt', password: 'ubnt' },
    { username: 'ubnt', password: 'agwist2017' },
    { username: 'ubnt', password: '-Agwist2017' },
    { username: 'ubnt', password: 'Agwist1.' }
];

console.log('Device API starting...');

async function getDeviceInfo(ssh, deviceType) {
    let info = {};

    try {
        if (deviceType === 'mikrotik') {
            // Obtener información de señal
            let result = await ssh.execCommand('/interface wireless registration-table print');
            info.signalStrength = result.stdout.trim() || 'No disponible';

            // Obtener rate de ether1
            result = await ssh.execCommand('/interface ethernet monitor ether1 once do={:put ($"rate")}');
            info.etherRate = result.stdout.trim() || 'No disponible';

            // Obtener lista de direcciones ARP
            result = await ssh.execCommand(':foreach i in=[/ip arp find where dynamic=yes and complete=yes] do={ :put [/ip arp get $i address] }');
            info.arpList = result.stdout
                .split('\n')
                .map(ip => ip.trim().replace(/\r/g, ''))  // Eliminar \r y espacios en blanco
                .filter(ip => ip && /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(ip))  // Filtrar IPs válidas
                .sort((a, b) => {
                    const aNum = a.split('.').map((num, idx) => parseInt(num) * Math.pow(256, 3-idx)).reduce((sum, num) => sum + num);
                    const bNum = b.split('.').map((num, idx) => parseInt(num) * Math.pow(256, 3-idx)).reduce((sum, num) => sum + num);
                    return aNum - bNum;
                });
                
            // Generar resumen de IPs por tercer octeto
            if (info.arpList.length > 10) {
                const ipSummary = info.arpList.reduce((acc, ip) => {
                    const subnet = ip.split('.').slice(0, 3).join('.') + '.0/24';
                    acc[subnet] = (acc[subnet] || 0) + 1;
                    return acc;
                }, {});
                info.ipSummary = Object.entries(ipSummary)
                    .sort((a, b) => b[1] - a[1]) // Ordenar por cantidad, de mayor a menor
                    .map(([subnet, count]) => `${subnet}: ${count}`);
            }
                

        } else if (deviceType === 'ubiquiti') {
            // Obtener información de señal
            let result = await ssh.execCommand('mca-status | grep signal');
            info.signalStrength = result.stdout.trim() || 'No disponible';

            // Obtener rate de eth0
            result = await ssh.execCommand('ethtool eth0 | grep Speed');
            info.etherRate = result.stdout.trim() || 'No disponible';

            // Obtener lista de direcciones ARP
            console.log('Ejecutando comando ARP en Ubiquiti');
            result = await ssh.execCommand('ip neigh show | grep -E "lladdr [0-9a-f]{2}(:[0-9a-f]{2}){5}" | grep -E "REACHABLE|STALE" | awk \'{print $1}\'');
            console.log('Resultado del comando ARP:', result.stdout);
            
            info.arpList = result.stdout.trim().split('\n').filter(Boolean) || [];
            
            // Si el resultado está vacío, intentar un enfoque alternativo
            if (info.arpList.length === 0) {
                console.log('Intentando enfoque alternativo para ARP en Ubiquiti');
                result = await ssh.execCommand('arp -e | tail -n +2 | awk \'{print $1}\'');
                console.log('Resultado del enfoque alternativo:', result.stdout);
                info.arpList = result.stdout.trim().split('\n').filter(Boolean) || [];
            }

        }
    } catch (error) {
        console.error(`Error getting device info: ${error.message}`);
        info.error = `Error: ${error.message}`;
    }

    console.log(`Device info for ${deviceType}:`, info);
    return info;
}

app.post('/execute-command', async (req, res) => {
    const { ip, deviceType } = req.body;
    console.log(`Received request for ${deviceType} device at ${ip}`);
    
    try {
        const credentials = deviceType === 'mikrotik' ? MIKROTIK_CREDENTIALS : UBIQUITI_CREDENTIALS;
        console.log(`Attempting connection with ${credentials.length} sets of credentials`);
        
        for (const cred of credentials) {
            try {
                console.log(`Trying ${cred.username}:${cred.password}`);
                const ssh = new NodeSSH();
                await ssh.connect({
                    host: ip,
                    username: cred.username,
                    password: cred.password,
                    tryKeyboard: true,
                    timeout: 20000,
                    algorithms: {
                        kex: ['diffie-hellman-group1-sha1', 'diffie-hellman-group14-sha1', 'diffie-hellman-group-exchange-sha1', 'diffie-hellman-group-exchange-sha256'],
                        cipher: ['3des-cbc', 'aes128-cbc', 'aes192-cbc', 'aes256-cbc', 'aes128-ctr', 'aes192-ctr', 'aes256-ctr']
                    },
                    hostVerifier: () => true,
                    agentForward: false,
                    agent: false,
                    useAgent: false,
                    privateKey: null,
                });
                
                console.log('SSH connection successful, executing commands');
                const deviceInfo = await getDeviceInfo(ssh, deviceType);
                console.log('Commands executed, device info:', deviceInfo);
                ssh.dispose();
                
                return res.json({ success: true, deviceInfo });
            } catch (error) {
                console.log(`Failed to connect or execute commands with ${cred.username}: ${error.message}`);
            }
        }
        
        throw new Error('All connection attempts failed');
    } catch (error) {
        console.error(`Error processing request for ${ip}:`, error);
        res.status(500).json({ success: false, error: error.message });
    }
});

app.get('/test', (req, res) => {
    res.json({ message: 'API is working' });
});
const PORT = process.env.API_PORT || 3124;
app.listen(PORT, () => console.log(`Device API running on port ${PORT}`));