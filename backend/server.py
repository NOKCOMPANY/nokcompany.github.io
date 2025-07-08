from flask import Flask, request
import subprocess
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite que tu frontend (GitHub Pages) acceda a este backend

@app.route("/run", methods=["POST"])
def run_command():
    data = request.get_json()
    command = data.get("command")

    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return result.decode("utf-8")
    except subprocess.CalledProcessError as e:
        return e.output.decode("utf-8"), 500

if __name__ == "__main__":
    app.run(port=5000)
