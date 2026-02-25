import os
import json
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
ZALO_API_BASE = "https://bot-api.zaloplatforms.com"

# ============================================
# 1. HEALTH CHECK ENDPOINTS
# ============================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "zalo-bot",
        "port": 5002,
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/health', methods=['GET'])
def api_health():
    """API health check"""
    return jsonify({
        "status": "ok",
        "message": "Zalo Bot API is running",
        "port": 5002
    }), 200


# ============================================
# 2. BOT INFO ENDPOINTS
# ============================================

@app.route('/api/bot/info', methods=['GET'])
def get_bot_info():
    """Get bot information"""
    try:
        url = f"{ZALO_API_BASE}/bot{BOT_TOKEN}/getMe"
        response = requests.post(url, json={})

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({
                "ok": False,
                "error": "Failed to get bot info"
            }), response.status_code
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500


# ============================================
# 3. WEBHOOK ENDPOINTS
# ============================================

@app.route('/api/webhook/set', methods=['POST'])
def set_webhook():
    """Set webhook URL"""
    try:
        data = request.get_json()
        webhook_url = data.get('url')

        if not webhook_url:
            return jsonify({
                "ok": False,
                "error": "URL is required"
            }), 400

        url = f"{ZALO_API_BASE}/bot{BOT_TOKEN}/setWebhook"
        payload = {
            "url": webhook_url,
            "secret_token": WEBHOOK_SECRET
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({
                "ok": False,
                "error": "Failed to set webhook"
            }), response.status_code
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500


@app.route('/api/webhook/info', methods=['GET'])
def get_webhook_info():
    """Get webhook information"""
    try:
        url = f"{ZALO_API_BASE}/bot{BOT_TOKEN}/getWebhookInfo"
        response = requests.post(url, json={})

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({
                "ok": False,
                "error": "Failed to get webhook info"
            }), response.status_code
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500


# ============================================
# 4. MESSAGE SENDING ENDPOINTS
# ============================================

@app.route('/api/message/send', methods=['POST'])
def send_message():
    """Send text message"""
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')
        text = data.get('text')

        if not chat_id or not text:
            return jsonify({
                "ok": False,
                "error": "chat_id and text are required"
            }), 400

        url = f"{ZALO_API_BASE}/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({
                "ok": False,
                "error": "Failed to send message"
            }), response.status_code
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500


@app.route('/api/message/photo', methods=['POST'])
def send_photo():
    """Send photo message"""
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')
        photo_url = data.get('photo')
        caption = data.get('caption', '')

        if not chat_id or not photo_url:
            return jsonify({
                "ok": False,
                "error": "chat_id and photo are required"
            }), 400

        url = f"{ZALO_API_BASE}/bot{BOT_TOKEN}/sendPhoto"
        payload = {
            "chat_id": chat_id,
            "photo": photo_url,
            "caption": caption
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({
                "ok": False,
                "error": "Failed to send photo"
            }), response.status_code
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500


@app.route('/api/message/sticker', methods=['POST'])
def send_sticker():
    """Send sticker message"""
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')
        sticker = data.get('sticker')

        if not chat_id or not sticker:
            return jsonify({
                "ok": False,
                "error": "chat_id and sticker are required"
            }), 400

        url = f"{ZALO_API_BASE}/bot{BOT_TOKEN}/sendSticker"
        payload = {
            "chat_id": chat_id,
            "sticker": sticker
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({
                "ok": False,
                "error": "Failed to send sticker"
            }), response.status_code
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500


# ============================================
# 5. CHAT ACTION ENDPOINTS
# ============================================

@app.route('/api/chat/action', methods=['POST'])
def send_chat_action():
    """Send chat action (typing, upload_photo)"""
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')
        action = data.get('action', 'typing')

        if not chat_id:
            return jsonify({
                "ok": False,
                "error": "chat_id is required"
            }), 400

        # Validate action
        valid_actions = ['typing', 'upload_photo']
        if action not in valid_actions:
            return jsonify({
                "ok": False,
                "error": f"Invalid action. Must be one of: {', '.join(valid_actions)}"
            }), 400

        url = f"{ZALO_API_BASE}/bot{BOT_TOKEN}/sendChatAction"
        payload = {
            "chat_id": chat_id,
            "action": action
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({
                "ok": False,
                "error": "Failed to send chat action"
            }), response.status_code
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500


# ============================================
# 6. WEBHOOK RECEIVER ENDPOINT
# ============================================

@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive webhook from Zalo"""
    try:
        # Verify secret token
        secret_token = request.headers.get('X-Bot-Api-Secret-Token')
        if secret_token != WEBHOOK_SECRET:
            return jsonify({
                "ok": False,
                "error": "Invalid secret token"
            }), 401

        data = request.get_json()

        # Log received message
        print(f"[WEBHOOK] Received: {json.dumps(data, indent=2)}")

        # Process message
        if data.get('event') == 'user_send_text':
            handle_text_message(data)
        elif data.get('event') == 'user_send_photo':
            handle_photo_message(data)

        return jsonify({"ok": True}), 200
    except Exception as e:
        print(f"[ERROR] Webhook error: {str(e)}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500


def handle_text_message(data):
    """Handle text message from user"""
    try:
        chat_id = data.get('sender', {}).get('id')
        text = data.get('message', {}).get('text', '')

        if not chat_id:
            return

        # Echo message back
        response_text = f"Bạn vừa gửi: {text}"

        url = f"{ZALO_API_BASE}/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": response_text
        }

        requests.post(url, json=payload)
    except Exception as e:
        print(f"[ERROR] Handle text message error: {str(e)}")


def handle_photo_message(data):
    """Handle photo message from user"""
    try:
        chat_id = data.get('sender', {}).get('id')

        if not chat_id:
            return

        # Send response
        response_text = "Cảm ơn bạn đã gửi ảnh!"

        url = f"{ZALO_API_BASE}/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": response_text
        }

        requests.post(url, json=payload)
    except Exception as e:
        print(f"[ERROR] Handle photo message error: {str(e)}")


# ============================================
# 7. ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "ok": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "ok": False,
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5002))
    print("\n" + "="*60)
    print("🤖 ZALO BOT SERVICE")
    print("="*60)
    print(f"Running on http://0.0.0.0:{port}")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)
