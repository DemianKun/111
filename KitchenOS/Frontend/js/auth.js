const API_URL = "http://localhost:8000";

// Intercambio entre Login y Registro
function toggleAuth(type) {
    const loginForm = document.getElementById('form-login');
    const registerForm = document.getElementById('form-register');
    const btnL = document.getElementById('btn-login');
    const btnR = document.getElementById('btn-register');

    if (type === 'login') {
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
        btnL.classList.add('tab-active');
        btnR.classList.remove('tab-active');
    } else {
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
        btnR.classList.add('tab-active');
        btnL.classList.remove('tab-active');
    }
}

// LOGIN: Solución al Error 400
async function login() {
    const u = document.getElementById('user-l').value;
    const p = document.getElementById('pass-l').value;

    const formData = new URLSearchParams();
    formData.append('username', u);
    formData.append('password', p);

    try {
        const res = await fetch(`${API_URL}/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        if (res.ok) {
            const data = await res.json();
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('username', u);
            window.location.href = 'chef_panel.html';
        } else {
            alert("Acceso denegado: Usuario o contraseña incorrectos.");
        }
    } catch (e) { console.error("Error:", e); }
}

// REGISTRO DE NUEVOS USUARIOS
async function register() {
    const user = document.getElementById('user-r').value;
    const pass = document.getElementById('pass-r').value;
    const rol = document.getElementById('role-r').value;

    try {
        const res = await fetch(`${API_URL}/api/usuarios/registro`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user, password: pass, rol: rol })
        });

        if (res.ok) {
            alert("Usuario creado con éxito. Ya puedes iniciar sesión.");
            toggleAuth('login');
        } else {
            const error = await res.json();
            alert(error.detail);
        }
    } catch (e) { alert("Error al conectar con el servidor."); }
}