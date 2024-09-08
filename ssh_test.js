const { NodeSSH } = require('node-ssh');

const CREDENTIALS = [
    { username: 'admin', password: 'agwist2017' }
];

async function testSSHConnection(ip, credentials) {
    console.log(`Testing SSH connection to ${ip}`);
    const ssh = new NodeSSH();

    for (const cred of credentials) {
        try {
            console.log(`Attempting connection with ${cred.username}:${cred.password}`);
            await ssh.connect({
                host: ip,
                username: cred.username,
                password: cred.password,
                tryKeyboard: true,
                timeout: 20000, // 20 segundos de timeout
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
            console.log(`Successfully connected to ${ip} with ${cred.username}`);
            
            // Ejecutar un comando simple
            console.log('Executing command...');
            const result = await ssh.execCommand('/system resource print');
            console.log('Command executed successfully');
            console.log('STDOUT:', result.stdout);
            console.log('STDERR:', result.stderr);
            
            ssh.dispose();
            return;
        } catch (error) {
            console.log(`Connection failed with ${cred.username}: ${error.message}`);
            if (error.stack) {
                console.log('Error stack:', error.stack);
            }
        }
    }
    console.log('All connection attempts failed');
}

async function runTest() {
    await testSSHConnection('192.168.26.120', CREDENTIALS);
}

runTest().catch(console.error);