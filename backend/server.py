from flask import Flask, request, jsonify
import subprocess
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Lista blanca de comandos permitidos. Usar un set es más eficiente para búsquedas.
ALLOWED_COMMANDS = {'ls', 'mkdir', 'date', 'pwd', 'whoami', 'status', 'cd'} 

# Diccionario de usuarios (en producción usar una base de datos y contraseñas cifradas)
USERS = {
    "admin": "123456",  # cambiar por contraseña segura
    "user1": "pass1"
}

def authenticate(request):
    auth = request.authorization
    if not auth:
        return False
    username = auth.username
    password = auth.password
    return USERS.get(username) == password

@app.route("/run", methods=["POST"])
def run_command():
    if not authenticate(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    command = data.get("command")

    if not command:
        return jsonify({"error": "No command provided"}), 400

    # Comando especial para verificar el estado del servidor de forma segura
    if command.strip() == 'status':
        return jsonify({"status": "active", "message": "Servidor online."})

    # --- PARSEO SEGURO DE COMANDOS ---
    # Dividir el comando y sus argumentos.
    command_parts = command.strip().split()
    base_command = command_parts[0]

    # Validar que el comando base esté en la lista blanca.
    if base_command not in ALLOWED_COMMANDS:
        return jsonify({"error": "Comando no permitido! 403"}), 403

    try:
        # Ejecutar el comando de forma segura, sin shell=True, pasando los argumentos como una lista.
        # Esto previene la inyección de comandos (ej: "ls; rm -rf /").
        result = subprocess.check_output(command_parts, stderr=subprocess.STDOUT)
        return result.decode("utf-8")
    except subprocess.CalledProcessError as e:
        return e.output.decode("utf-8"), 500
    except FileNotFoundError:
        return f"Comando no encontrado: {base_command}", 404

if __name__ == "__main__":
    # Esta línea te confirmará que el servidor se está iniciando.
    print("🚀 Servidor Flask iniciándose en http://0.0.0.0:5000")
    # Esta línea inicia el servidor y lo mantiene escuchando peticiones.
    app.run(host="0.0.0.0", port=5000, debug=True)
