from flask import Flask, jsonify
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "running",
        "bot_status": "online",
        "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "1.0.1"
    }), 200

@app.route('/')
def index():
    return "Zalo Flask API is running on port 5001"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
