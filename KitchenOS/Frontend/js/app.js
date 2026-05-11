const API_URL = "http://localhost:8000";
let ingredientesNuevaReceta = {}; // Memoria temporal para la receta didáctica

// --- UTILIDADES ---
setInterval(() => { document.getElementById('live-clock').innerText = new Date().toLocaleTimeString(); }, 1000);

function showSec(id, btnElement) {
    document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('nav-active'));
    document.getElementById(id).classList.remove('hidden');
    if(btnElement) btnElement.classList.add('nav-active');

    if(id === 'sec-inv') loadConfigEditor();
    if(id === 'sec-recetas') { loadRecipes(); updateIngredienteSelect(); }
}

// --- DASHBOARD ---
async function loadDashboard() {
    const token = localStorage.getItem('access_token');
    if(!token) { window.location.href = 'index.html'; return; }

    try {
        const res = await fetch(`${API_URL}/api/dashboard/mapeado`, { headers: { 'Authorization': `Bearer ${token}` } });
        const data = await res.json();
        document.getElementById('welcome-msg').innerText = `Chef ${localStorage.getItem('username') || ''}`;
        document.getElementById('txt-temp').innerText = `${data.temperatura.toFixed(1)}°C`;

        const container = document.getElementById('barras-mapeadas');
        container.innerHTML = data.inventario.map(item => `
            <div>
                <div class="flex justify-between text-[10px] font-bold mb-1 uppercase text-slate-400">
                    <span class="text-white">${item.nombre}</span>
                    <span class="text-orange-500">${item.peso.toFixed(2)} KG</span>
                </div>
                <div class="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                    <div class="bg-gradient-to-r from-orange-600 to-orange-400 h-full transition-all duration-700" 
                         style="width: ${Math.min((item.peso / 5) * 100, 100)}%"></div>
                </div>
            </div>
        `).join('');

        loadTareas(token);
    } catch (e) { console.log("Reconectando..."); }
}

async function loadTareas(token) {
    const res = await fetch(`${API_URL}/api/tareas/activas`, { headers: { 'Authorization': `Bearer ${token}` } });
    const tareas = await res.json();
    const container = document.getElementById('contenedor-tareas');
    if(tareas.length === 0) { container.innerHTML = `<p class="text-[10px] text-slate-500 italic">Esperando órdenes de la IA...</p>`; return; }
    container.innerHTML = tareas.map(t => `
        <div class="bg-black/50 p-4 rounded-xl border-l-4 border-l-orange-500 shadow-lg">
            <p class="text-xs font-black text-white">${t.receta}</p>
            <p class="text-[9px] text-orange-400 font-bold uppercase mt-1">${t.cocinero} - ${t.estado}</p>
        </div>
    `).join('');
}

// --- CONFIGURACIÓN DE SENSORES ---
async function loadConfigEditor() {
    const res = await fetch(`${API_URL}/api/inventario/config`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` } });
    const configs = await res.json();
    document.getElementById('editor-basculas').innerHTML = configs.map(c => `
        <div class="flex items-center gap-4 bg-black/40 p-4 rounded-2xl border border-white/5">
            <span class="text-orange-500 font-mono text-[10px] w-16 uppercase">${c.id_bascula}</span>
            <input id="in-name-${c.id_bascula}" type="text" value="${c.nombre_producto}" class="bg-transparent border-b border-white/10 outline-none flex-1 text-sm text-white focus:border-orange-500">
            <button onclick="saveSensorName('${c.id_bascula}')" class="bg-orange-500 text-white text-[10px] px-4 py-2 rounded-lg font-bold hover:bg-orange-400 transition-all">ACTUALIZAR</button>
        </div>
    `).join('');
}

async function saveSensorName(id_bascula) {
    const name = document.getElementById(`in-name-${id_bascula}`).value;
    const res = await fetch(`${API_URL}/api/inventario/config/${id_bascula}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('access_token')}` },
        body: JSON.stringify({ nombre_producto: name, stock_minimo: 0.5 })
    });
    if(res.ok) alert("Configuración guardada en MySQL");
}

// --- RECETARIO DIDÁCTICO ---
function addIngredienteLista() {
    const ing = document.getElementById('sel-ingrediente').value;
    const cant = parseFloat(document.getElementById('num-cantidad').value);
    if(!ing || !cant) return;
    ingredientesNuevaReceta[ing] = cant;
    renderIngredientesTemp();
}

function renderIngredientesTemp() {
    const container = document.getElementById('lista-ingredientes-temp');
    container.innerHTML = Object.entries(ingredientesNuevaReceta).map(([i, c]) => `
        <span class="bg-blue-500/20 text-blue-300 text-[9px] px-2 py-1 rounded-md mr-1 mb-1 font-bold">${i}: ${c}kg</span>
    `).join('');
}

async function updateIngredienteSelect() {
    const res = await fetch(`${API_URL}/api/inventario/config`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` } });
    const configs = await res.json();
    document.getElementById('sel-ingrediente').innerHTML = configs.map(c => `<option value="${c.nombre_producto}">${c.nombre_producto}</option>`).join('');
}

async function loadRecipes() {
    const res = await fetch(`${API_URL}/api/recetas`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` } });
    const recetas = await res.json();
    document.getElementById('contenedor-recetas').innerHTML = recetas.map(r => `
        <div class="bg-black/40 p-6 rounded-[1.5rem] border border-white/5 hover:border-orange-500/30 transition-colors">
            <h5 class="text-xl font-black text-white mb-2">${r.nombre}</h5>
            <div class="flex flex-wrap gap-2 mb-4">
                ${Object.entries(r.ingredientes_json).map(([i, c]) => `<span class="bg-orange-500/10 text-orange-400 text-[10px] px-2 py-1 rounded-lg border border-orange-500/20">${i}: ${c}kg</span>`).join('')}
            </div>
            <p class="text-[11px] text-slate-400">${r.descripcion}</p>
        </div>
    `).join('');
}

async function guardarRecetaFinal() {
    const payload = {
        nombre: document.getElementById('rec-nombre').value,
        descripcion: document.getElementById('rec-desc').value,
        ingredientes_json: ingredientesNuevaReceta
    };
    const res = await fetch(`${API_URL}/api/recetas`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('access_token')}` },
        body: JSON.stringify(payload)
    });
    if(res.ok) { alert("Receta Sincronizada"); ingredientesNuevaReceta = {}; showSec('sec-dash'); }
}

// INICIO
if(window.location.pathname.includes('chef_panel')) {
    loadDashboard();
    setInterval(loadDashboard, 5000);
}