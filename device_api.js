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

async function getSignalStrength(ssh, deviceType) {
    let command;
    if (deviceType === 'mikrotik') {
        command = '/interface wireless registration-table print';
    } else if (deviceType === 'ubiquiti') {
        command = 'mca-status | grep signal';
    }

    console.log(`Executing command on ${deviceType}: ${command}`);
    const result = await ssh.execCommand(command);
    console.log(`Command result: ${result.stdout}`);
    return result.stdout;
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
                
                console.log('SSH connection successful, executing command');
                const signalStrength = await getSignalStrength(ssh, deviceType);
                console.log('Command executed, signal strength:', signalStrength);
                ssh.dispose();
                
                return res.json({ success: true, signalStrength });
            } catch (error) {
                console.log(`Failed to connect with ${cred.username}: ${error.message}`);
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