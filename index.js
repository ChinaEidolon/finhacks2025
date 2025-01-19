const express = require('express');
const path = require('path');
const app = express();
const port = 3000;
const { WebSocketServer } = require('ws');
const { PythonShell } = require('python-shell');
const https = require('https');
const http = require('http');
const fs = require('fs');

let server;

// Try to read SSL certificates if they exist
try {
    const privateKey = fs.readFileSync('path/to/private-key.pem', 'utf8');
    const certificate = fs.readFileSync('path/to/certificate.pem', 'utf8');
    const credentials = { key: privateKey, cert: certificate };
    // Create HTTPS server if certificates are available
    server = https.createServer(credentials, app);
    console.log('Running server in HTTPS mode');
} catch (error) {
    // Fall back to HTTP if certificates are not available
    server = http.createServer(app);
    console.log('Running server in HTTP mode (SSL certificates not found)');
}

// Serve static files from the current directory
app.use(express.static(__dirname));

// Route for the homepage
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'webpage.html'));
});

// Start the server (works for both HTTP and HTTPS)
server.listen(port, () => {
    const protocol = server instanceof https.Server ? 'https' : 'http';
    console.log(`Server running at ${protocol}://localhost:${port}`);
});

// Create WebSocket server attached to the server
const wss = new WebSocketServer({ 
    server: server,
    host: '0.0.0.0'
});

const clients = new Set();

wss.on('connection', (ws) => {
    clients.add(ws);
    
    // Send current users to new client
    const users = Array.from(clients)
        .map(client => client.username)
        .filter(Boolean);
    ws.send(JSON.stringify({ type: 'users', users }));

    ws.on('message', async (message) => {
        const data = JSON.parse(message);
        console.log('Received message:', data); // Debug log
        
        if (data.type === 'username') {
            ws.username = data.username;
            // Broadcast new user to all clients
            clients.forEach(client => {
                if (client !== ws && client.readyState === 1) {
                    client.send(JSON.stringify({
                        type: 'username',
                        username: data.username
                    }));
                }
            });
        } else if (data.type === 'money') {
            try {
                const options = {
                    mode: 'text',
                    pythonPath: 'python3',
                    pythonOptions: ['-u'],
                    scriptPath: __dirname,
                    args: [data.amount.toString()]
                };

                PythonShell.run('python_encryption.py', options, function (err, results) {
                    if (err) {
                        console.error('Python Error:', err);
                        return;
                    }
                    
                    console.log('Python Results:', results);
                    
                    if (results && results.length >= 2) {
                        const encryptedAmount = results[results.length - 2];
                        const decryptedAmount = parseInt(results[results.length - 1]);
                        
                        // Broadcast to ALL connected clients
                        clients.forEach(client => {
                            if (client.readyState === 1) {  // Check if client connection is open
                                client.send(JSON.stringify({
                                    type: 'money',
                                    recipientUsername: data.recipientUsername,
                                    amount: decryptedAmount,
                                    encryptedAmount: encryptedAmount
                                }));
                            }
                        });
                    }
                });
            } catch (error) {
                console.error('Error processing money transfer:', error);
            }
        }
    });

    ws.on('close', () => {
        clients.delete(ws);
    });
});

