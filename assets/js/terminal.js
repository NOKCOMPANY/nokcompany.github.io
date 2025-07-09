document.addEventListener('DOMContentLoaded', () => {
    // --- Configuration ---
    const serverURL = "https://midominiopersonal.loca.lt/run";

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
    
    const predefinedCommandButtons = document.querySelectorAll('#protectedContent .btn[data-command]');

    // --- Functions ---

    /**
     * Gets the Basic Auth header value from the form inputs.
     * @returns {string} The Authorization header value.
     */
    function getAuthHeader() {
        const user = usernameInput.value;
        const pass = passwordInput.value;
        return "Basic " + btoa(`${user}:${pass}`);
    }

    /**
     * Executes a command on the server.
     * @param {string} command - The command to execute.
     */
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
                // Try to parse error from JSON if possible, otherwise use the raw text
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

    /**
     * Handles the login process by switching the UI.
     * NOTE: This is for UI purposes only. Real authentication happens on the server for each command.
     */
    function handleLogin() {
        // The original client-side check was insecure and has been removed.
        // We now rely on the server to authenticate each command via the Authorization header.
        // This function just handles the UI transition.
        loginForm.classList.add("fade-out");
        setTimeout(() => {
            loginForm.style.display = "none";
            protectedContent.style.display = "block";
        }, 500);
    }

    /**
     * Handles the logout process.
     */
    function handleLogout() {
        protectedContent.style.display = "none";
        loginForm.style.display = "block";
        loginForm.classList.remove("fade-out");
        // Clear dynamic content and state
        customButtonContainer.innerHTML = "";
        outputElement.innerText = "Esperando comando...";
        terminalInput.value = "";
    }

    /**
     * Adds a new custom command button to the UI.
     */
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

        // Clear inputs
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
});