from flask import Flask, request, jsonify
import subprocess
from flask_cors import CORS
import os
import csv
import shlex
from werkzeug.utils import secure_filename
import requests

app = Flask(__name__)
CORS(app)

# Clave del servicio de correo almacenada como variable de entorno
EMAILJS_PUBLIC_KEY = os.environ.get("EMAILJS_PUBLIC_KEY")

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
    # Dividir el comando y sus argumentos utilizando shlex para respetar comillas
    try:
        command_parts = shlex.split(command)
    except ValueError as e:
        return jsonify({"error": f"Invalid command: {str(e)}"}), 400

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

@app.route("/files", methods=["GET"])
def list_files():
    if not authenticate(request):
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        current_dir = '.' 
        files = [f for f in os.listdir(current_dir) if os.path.isfile(os.path.join(current_dir, f))]
        return jsonify(files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/read_csv", methods=["GET"])
def read_csv_file():
    if not authenticate(request):
        return jsonify({"error": "Unauthorized"}), 401

    filename = request.args.get('file')
    if not filename:
        return jsonify({"error": "Filename not provided"}), 400

    # Seguridad: Sanitiza el nombre del archivo para prevenir Path Traversal
    safe_filename = secure_filename(filename)
    if safe_filename != filename:
        return jsonify({"error": "Invalid filename"}), 400

    # Seguridad: Asegura que el archivo esté en el directorio actual
    current_dir = os.path.abspath('.')
    file_path = os.path.abspath(os.path.join(current_dir, safe_filename))

    if not file_path.startswith(current_dir):
        return jsonify({"error": "Access denied"}), 403

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        rows = []
        with open(file_path, mode='r', encoding='utf-8', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                rows.append(row)
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": f"Error reading CSV file: {str(e)}"}), 500


@app.route("/send-email", methods=["POST"])
def send_email():
    data = request.get_json()
    nombre = data.get("nombre")
    correo = data.get("correo")
    mensaje = data.get("mensaje")

    if not EMAILJS_PUBLIC_KEY:
        return jsonify({"error": "Email service key not configured"}), 500

    payload = {
        "service_id": "NOKCOMPANY",
        "template_id": "template_jbnt66h",
        "user_id": EMAILJS_PUBLIC_KEY,
        "template_params": {
            "nombre": nombre,
            "correo": correo,
            "mensaje": mensaje,
        },
    }

    try:
        response = requests.post(
            "https://api.emailjs.com/api/v1.0/email/send", json=payload
        )
        if response.status_code == 200:
            return jsonify({"success": True})
        return jsonify({"error": "Failed to send email"}), 500
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Esta línea te confirmará que el servidor se está iniciando.
    print("🚀 Servidor Flask iniciándose en http://0.0.0.0:80 (Requiere sudo para ejecutar)")
    # Esta línea inicia el servidor y lo mantiene escuchando peticiones.
    app.run(host="0.0.0.0", port=80, debug=True)
