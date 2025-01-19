const express = require('express');
const path = require('path');
const app = express();
const port = 3000;
const { WebSocketServer } = require('ws');
const { PythonShell } = require('python-shell');



// Serve static files from the current directory
app.use(express.static(__dirname));

// Route for the homepage
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'webpage.html'));
});

// Start the server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});


const wss = new WebSocketServer({ 
    port: 8080,
    host: '0.0.0.0'  // Listen on all available network interfaces
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
                    
                    console.log('Python Results:', results); // Debug log
                    
                    if (results && results.length >= 2) {
                        const encryptedAmount = results[results.length - 2];
                        const decryptedAmount = parseInt(results[results.length - 1]);
                        
                        // Broadcast to all clients to ensure everyone's display updates
                        clients.forEach(client => {
                            if (client.readyState === 1) {
                                client.send(JSON.stringify({
                                    type: 'money',
                                    recipientUsername: data.recipientUsername,
                                    amount: decryptedAmount,
                                    encryptedAmount: encryptedAmount,
                                    currentAmount: data.currentAmount || 0
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

