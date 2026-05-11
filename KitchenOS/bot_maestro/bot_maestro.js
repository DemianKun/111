const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// --- TUS NÚMEROS OFICIALES ---
const numeroChef = '5215529469944@c.us'; // Tú
let grupoCocina = '120363407473241114@g.us'; // Grupo de Cocina
const numeroProveedor = '5215564543209@c.us'; // Proveedor

// Inicializamos el motor de WhatsApp
const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: { headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox'] }
});

client.on('qr', (qr) => { 
    console.log("📱 ESCANEA ESTE QR PARA INICIAR EL BOT MAESTRO:");
    qrcode.generate(qr, { small: true }); 
});

client.on('ready', () => {
    console.log('✅ [BOT K-OS] Conectado exitosamente. Las 3 IAs están operativas en la red de Meta.');
});

// --- EL OÍDO DEL BOT (Escuchar comandos y avisar a Python) ---
client.on('message', async (msg) => {
    const texto = msg.body.trim().toUpperCase();
    
    // Filtramos para ignorar conversaciones normales, solo buscamos palabras clave
    if (texto.startsWith('CONFIRMO') || texto === 'ACEPTO' || texto === 'YO') {
        console.log(`📩 Comando detectado de ${msg.from}: ${texto}`);

        try {
            // Mandamos los datos al Webhook del Cerebro (Python)
            await axios.post('http://localhost:8000/api/whatsapp/webhook', {
                numero: msg.from,
                texto: texto
            });

            // Respuestas amables en WhatsApp para dar retroalimentación inmediata
            if (texto.startsWith('CONFIRMO')) {
                msg.reply("✅ Autorización validada por KitchenOS. Solicitando orden de compra al proveedor...");
            } else {
                msg.reply("✅ Asignación pre-aprobada. Por favor, confirma tu inicio en la pantalla táctil de tu estación.");
            }
        } catch (error) {
            console.error("❌ Error de comunicación: El cerebro central (Python) no responde al Webhook.");
        }
    }
});

// --- EL MEGÁFONO DEL BOT (Recibir órdenes de Python y rutearlas por WhatsApp) ---
app.post('/api/enviar', async (req, res) => {
    const { tipo, mensaje } = req.body;
    
    try {
        if (tipo === 'alerta_stock') {
            // RUTA 1: IA Vigilante -> Avisa al Chef
            await client.sendMessage(numeroChef, mensaje);
            console.log(`📤 [IA Vigilante] Alerta de inventario enviada al Chef.`);
            
        } else if (tipo === 'propuesta') {
            // RUTA 2: IA Asignación -> Avisa al Grupo
            await client.sendMessage(grupoCocina, mensaje);
            console.log(`📤 [IA Asignación] Comanda lanzada al Grupo de Cocina.`);
            
        } else if (tipo === 'orden_compra') {
            // RUTA 3: IA Compras -> Pide mercancía al Proveedor
            await client.sendMessage(numeroProveedor, mensaje);
            console.log(`🛒 [IA Compras] Orden oficial de reabastecimiento enviada al Proveedor.`);
        }
        
        res.json({ status: 'enviado_ok' });
    } catch (error) {
        console.error('❌ Error crítico enviando mensaje a la red celular:', error.message);
        res.status(500).json({ error: 'Fallo al despachar en WhatsApp' });
    }
});

// Levantamos el servidor en el puerto 3000
app.listen(3000, () => { 
    console.log('🌐 Servidor del Bot Maestro activo en el puerto 3000'); 
});

// Arranca el navegador Chrome invisible
client.initialize();