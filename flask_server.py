from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import datetime
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
CORS(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["2000 per day", "500 per hour"],
    storage_uri="memory://"
)

messages = []

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/message/log', methods=['POST'])
def log_message():
    try:
        data = request.get_json()
        new_msg = {
            "sender_id": data.get("sender_id"),
            "sender_name": data.get("sender_name"),
            "text": data.get("text"),
            "timestamp": datetime.datetime.now().isoformat()
        }
        messages.append(new_msg)
        if len(messages) > 100: messages.pop(0)
        return jsonify({"ok": True}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route('/api/messages', methods=['GET'])
def get_messages():
    return jsonify({"messages": messages}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
