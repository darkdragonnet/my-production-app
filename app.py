from flask import Flask, jsonify, request
from datetime import datetime
import os
import logging
import requests
import json
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)
DB_FILE = os.path.join(os.path.dirname(__file__), 'data', 'webhooks.db')

app = Flask(__name__)

def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS webhooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_name TEXT, sender_id TEXT, message_text TEXT, raw_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()
    except Exception as e: logger.error(f"Lỗi DB: {e}")

init_db()

@app.route('/', methods=['GET'])
def home(): return jsonify({"message": "Zalo Bot API is running!"})

@app.route('/status', methods=['GET'])
def status(): return jsonify({"status": "online", "bot_status": "active", "version": "1.0.8"})

@app.route('/bot-info', methods=['GET'])
def get_bot_info():
    token = os.getenv('ZALO_BOT_TOKEN') or os.getenv('ZALO_ACCESS_TOKEN')
    if not token or token == 'YOUR_TOKEN_HERE': return jsonify({"ok": False, "error": "Thiếu token"}), 400
    try:
        res = requests.get(f"https://bot-api.zaloplatforms.com/bot{token}/getMe", timeout=5)
        return jsonify(res.json()) if res.status_code == 200 else jsonify({"ok": False}), 400
    except Exception as e: return jsonify({"ok": False, "error": str(e)}), 500

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET': return jsonify({"status": "webhook endpoint ready"})
    secret_token = request.headers.get("X-Bot-Api-Secret-Token")
    if secret_token != "GiaTruongBotSecretKey2026": return jsonify({"error": "Unauthorized"}), 403
    
    # 🔑 FIX: Xử lý JSON đúng chuẩn (Chống lỗi ký tự xuống dòng)
    try:
        data = request.get_json(silent=True)
        if data is None:
            # Nếu get_json thất bại do ký tự lạ, dùng json.loads thủ công
            raw_data = request.get_data(as_text=True)
            data = json.loads(raw_data, strict=False)
    except Exception as e:
        logger.error(f"Lỗi parse JSON: {e}")
        return jsonify({"error": "Invalid JSON"}), 400
        
    payload = data.get("result", data) 
    event_name = payload.get("event_name", "unknown")
    message_obj = payload.get("message", {})
    from_obj = message_obj.get("from", {})
    sender_id = from_obj.get("id", "")
    message_text = message_obj.get("text", "")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if sender_id:
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO webhooks (timestamp, event_name, sender_id, message_text, raw_data) VALUES (?, ?, ?, ?, ?)",
                      (timestamp, event_name, sender_id, message_text, json.dumps(data)))
            conn.commit()
            conn.close()
            logger.info(f"✅ Đã ghi Webhook vào Database (UID: {sender_id})")
        except Exception as e: logger.error(f"Lỗi DB: {e}")
    return jsonify({"message": "Success", "ok": True})

@app.route('/get-messages', methods=['GET'])
def get_messages():
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM webhooks ORDER BY id DESC LIMIT 50")
        rows = c.fetchall()
        conn.close()
        return jsonify({"messages": [dict(row) for row in rows]})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/followers', methods=['GET'])
def get_followers():
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""SELECT sender_id, MAX(timestamp) as last_active, COUNT(id) as interaction_count, raw_data
            FROM webhooks WHERE sender_id IS NOT NULL AND sender_id != '' GROUP BY sender_id ORDER BY last_active DESC""")
        rows = c.fetchall()
        conn.close()
        followers = []
        for row in rows:
            user_data = dict(row)
            display_name = "Không xác định"
            try:
                raw = json.loads(user_data.get("raw_data", "{}"))
                display_name = raw.get("result", raw).get("message", {}).get("from", {}).get("display_name", "Không xác định")
            except Exception: pass
            user_data["name"] = display_name
            user_data["avatar"] = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
            user_data.pop("raw_data", None)
            followers.append(user_data)
        return jsonify({"total_followers": len(followers), "followers": followers})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/send-message', methods=['POST'])
@app.route('/send_message', methods=['POST'])
@app.route('/api/send_message', methods=['POST'])
@app.route('/api/send-message', methods=['POST'])
def send_message():
    token = os.getenv('ZALO_BOT_TOKEN') or os.getenv('ZALO_ACCESS_TOKEN')
    if not token or token == 'YOUR_TOKEN_HERE': return jsonify({"error": "Thiếu token cấu hình"}), 400
    
    data = request.get_json()
    chat_id = data.get('chat_id') or data.get('recipient_id') 
    msg_type = data.get('type', 'text') 
    
    if not chat_id: return jsonify({"error": "Thiếu thông tin người nhận (chat_id)"}), 400
        
    headers = {"Content-Type": "application/json"}
    base_url = f"https://bot-api.zaloplatforms.com/bot{token}"

    try:
        requests.post(f"{base_url}/sendChatAction", headers=headers, json={"chat_id": chat_id, "action": "typing"}, timeout=2)
    except Exception as e:
        logger.warning(f"Bỏ qua lỗi timeout Đang gõ: {e}")
        
    payload = {"chat_id": chat_id}
    endpoint = ""
    
    if msg_type == 'text':
        endpoint = "/sendMessage"
        payload["text"] = data.get('text', data.get('message', ''))
    elif msg_type == 'photo':
        endpoint = "/sendPhoto"
        payload["photo"] = data.get('photo_url', '')
        if data.get('caption'): payload["caption"] = data.get('caption')
    elif msg_type == 'sticker':
        endpoint = "/sendSticker"
        payload["sticker"] = data.get('sticker_id', '')

    try:
        res = requests.post(f"{base_url}{endpoint}", headers=headers, json=payload, timeout=15)
        if res.status_code == 200:
            return jsonify({"status": "success", "result": res.json()})
        else:
            logger.error(f"Zalo API Error: {res.text}")
            return jsonify({"error": f"Từ chối từ Zalo: {res.text}"}), 400
    except Exception as e:
        logger.error(f"Lỗi gửi tin nhắn: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
