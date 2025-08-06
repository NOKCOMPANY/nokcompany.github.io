from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import csv
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

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

def get_system_status():
    """Return basic information about server status."""
    return {"status": "active", "message": "Servidor online."}


ALLOWED_ACTIONS = {
    "get_system_status": get_system_status,
}


@app.route("/run", methods=["POST"])
def run_action():
    if not authenticate(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    action = data.get("action")

    if not action:
        return jsonify({"error": "No action provided"}), 400

    func = ALLOWED_ACTIONS.get(action)
    if not func:
        return jsonify({"error": "Action not allowed"}), 403

    try:
        result = func()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
    # Esta línea te confirmará que el servidor se está iniciando.
    print("🚀 Servidor Flask iniciándose en http://0.0.0.0:80 (Requiere sudo para ejecutar)")
    # Esta línea inicia el servidor y lo mantiene escuchando peticiones.
    app.run(host="0.0.0.0", port=80, debug=True)
