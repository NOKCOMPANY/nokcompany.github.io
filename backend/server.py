from flask import Flask, request, jsonify
import subprocess
from flask_cors import CORS
import os
import csv
import shlex
from werkzeug.utils import secure_filename
import bcrypt

app = Flask(__name__)
CORS(app)

# Lista blanca de comandos permitidos. Usar un set es más eficiente para búsquedas.
ALLOWED_COMMANDS = {'ls', 'mkdir', 'date', 'pwd', 'whoami', 'status', 'cd'} 

# Las contraseñas se obtienen de variables de entorno como ADMIN_PASSWORD_HASH,
# USER1_PASSWORD_HASH, etc. Cada valor debe ser un hash generado con bcrypt.

def authenticate(request):
    auth = request.authorization
    if not auth:
        return False
    username = auth.username
    password = auth.password

    # Obtener el hash almacenado en la variable de entorno correspondiente
    env_var = f"{username.upper()}_PASSWORD_HASH"
    stored_hash = os.environ.get(env_var)
    if not stored_hash:
        return False

    try:
        return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
    except ValueError:
        # El hash almacenado no es válido
        return False

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

if __name__ == "__main__":
    # Inicia el servidor de desarrollo solo si se ejecuta directamente
    # FLASK_ENV=development habilita el modo debug.
    debug_mode = os.environ.get("FLASK_ENV") == "development"
    print("🚀 Servidor Flask iniciándose en http://0.0.0.0:80 (Requiere sudo para ejecutar)")
    # No usar en producción; en su lugar usar un servidor WSGI como Gunicorn.
    app.run(host="0.0.0.0", port=80, debug=debug_mode)
