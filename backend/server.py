from flask import Flask, request, jsonify
import subprocess
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Lista blanca de comandos permitidos
ALLOWED_COMMANDS = ['ls', 'mkdir', 'date', 'pwd', 'whoami']

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

    # Solo permitir comandos que estén en la whitelist
    if not any(command.strip().startswith(allowed) for allowed in ALLOWED_COMMANDS):
        return jsonify({"error": "Command not allowed"}), 403

    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return result.decode("utf-8")
    except subprocess.CalledProcessError as e:
        return e.output.decode("utf-8"), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
