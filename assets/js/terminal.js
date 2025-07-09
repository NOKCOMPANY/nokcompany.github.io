// terminal.js - Corrige la URL y mantén todo el resto igual
// ============================= ¡IMPORTANTE! =============================
// Reemplaza la siguiente URL con la que te entrega ngrok en tu terminal.
// Ejemplo: si ngrok te da "https://random-name-12345.ngrok-free.app",
// la URL aquí debe ser "https://random-name-12345.ngrok-free.app/run"
// ¡ASEGÚRATE DE QUE TERMINE EN /run!
const serverURL = "https://concise-friendly-sole.ngrok-free.app/run";

// --- DOM Elements ---
const loginForm = document.getElementById('loginForm');
const protectedContent = document.getElementById('protectedContent');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const loginButton = document.querySelector('#loginForm .btn-login');
const logoutButton = document.querySelector('#protectedContent .btn-outline-danger');

const terminalInput = document.getElementById('terminalInput');
const runCustomCommandButton = document.querySelector('.terminal-input-group .btn-success');
const outputElement = document.getElementById('output');

const customButtonContainer = document.getElementById('customButtonContainer');
const addCustomButtonBtn = document.querySelector('#addCustomButtonContainer .btn-info');
const customButtonLabelInput = document.getElementById('customButtonLabel');
const customButtonCommandInput = document.getElementById('customButtonCommand');

// --- Server Status Elements ---
const serverStatusIndicator = document.getElementById('serverStatusIndicator');
const serverStatusText = document.getElementById('serverStatusText');

// --- State ---
let statusInterval = null;

const predefinedCommandButtons = document.querySelectorAll('#protectedContent .btn[data-command]');

// --- Functions ---

function getAuthHeader() {
    const user = usernameInput.value;
    const pass = passwordInput.value;
    return "Basic " + btoa(`${user}:${pass}`);
}

async function checkServerStatus() {
    if (serverURL.includes("TU_URL_DE_NGROK_AQUI")) {
        serverStatusText.innerText = "Error: Configura la URL del servidor en terminal.js";
        serverStatusIndicator.classList.remove('online');
        serverStatusIndicator.classList.add('offline');
        return;
    }
    if (!serverURL.endsWith('/run')) {
        console.error("La serverURL no termina en /run. La conexión fallará.");
        serverStatusText.innerText = "Error: La URL en terminal.js está mal configurada.";
        return;
    }
    try {
        const response = await fetch(serverURL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": getAuthHeader()
            },
            body: JSON.stringify({ command: "status" })
        });

        if (response.ok) {
            const data = await response.json();
            serverStatusIndicator.classList.remove('offline');
            serverStatusIndicator.classList.add('online');
            serverStatusText.innerText = `Conectado - ${data.message || 'Servidor activo.'}`;
        } else {
            serverStatusIndicator.classList.remove('online');
            serverStatusIndicator.classList.add('offline');
            serverStatusText.innerText = `Error de conexión (Código: ${response.status})`;
        }
    } catch (error) {
        serverStatusIndicator.classList.remove('online');
        serverStatusIndicator.classList.add('offline');
        serverStatusText.innerText = "Desconectado - No se pudo alcanzar el servidor.";
    }
}

async function runCommand(command) {
    if (!command || command.trim() === "") {
        alert("Por favor, escribe un comando.");
        return;
    }
    outputElement.innerText = "Executing...";
    try {
        const response = await fetch(serverURL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": getAuthHeader()
            },
            body: JSON.stringify({ command })
        });

        const text = await response.text();

        if (!response.ok) {
            try {
                const errorJson = JSON.parse(text);
                throw new Error(errorJson.error || `Error del servidor: ${response.status}`);
            } catch (e) {
                throw new Error(text || `Error del servidor: ${response.status}`);
            }
        }
        outputElement.innerText = text;
    } catch (err) {
        outputElement.innerText = `Error: ${err.message}`;
    }
}

function handleLogin() {
    loginForm.classList.add("fade-out");
    setTimeout(() => {
        loginForm.style.display = "none";
        protectedContent.style.display = "block";
        checkServerStatus();
        statusInterval = setInterval(checkServerStatus, 10000);
    }, 500);
}

function handleLogout() {
    protectedContent.style.display = "none";
    loginForm.style.display = "block";
    loginForm.classList.remove("fade-out");
    customButtonContainer.innerHTML = "";
    outputElement.innerText = "Esperando comando...";
    terminalInput.value = "";
    clearInterval(statusInterval);
    serverStatusText.innerText = "Desconectado";
    serverStatusIndicator.classList.remove('online');
    serverStatusIndicator.classList.add('offline');
}

function addCustomButton() {
    const label = customButtonLabelInput.value.trim();
    const command = customButtonCommandInput.value.trim();
    if (!label || !command) {
        alert("Por favor, ingresa la etiqueta y el comando.");
        return;
    }
    const btn = document.createElement("button");
    btn.className = "btn btn-secondary";
    btn.style.marginRight = "8px";
    btn.innerText = label;
    btn.addEventListener('click', () => runCommand(command));
    customButtonContainer.appendChild(btn);
    customButtonLabelInput.value = "";
    customButtonCommandInput.value = "";
}

// --- Event Listeners ---
loginButton?.addEventListener('click', handleLogin);
logoutButton?.addEventListener('click', handleLogout);
runCustomCommandButton?.addEventListener('click', () => runCommand(terminalInput.value));
addCustomButtonBtn?.addEventListener('click', addCustomButton);

terminalInput?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        runCommand(terminalInput.value);
    }
});

predefinedCommandButtons.forEach(button => {
    button.addEventListener('click', () => {
        const command = button.dataset.command;
        runCommand(command);
    });
});
