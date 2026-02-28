from flask import Flask, request, jsonify
import os
import logging
import requests
import re
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("zalo_bot")
app = Flask(__name__)

FLASK_API_URL = os.getenv("FLASK_API_URL", "http://zalo-flask-api:5001")

def send_zalo_message(chat_id, text):
    try:
        payload = {"chat_id": chat_id, "type": "text", "text": text}
        requests.post(f"{FLASK_API_URL}/send-message", json=payload, timeout=15)
    except Exception as e:
        logger.error(f"❌ Lỗi nhờ Flask API gửi tin: {e}")

# ==========================================
# 🧠 GỌI THẲNG MAGISTERIUM (CHUẨN DOCS)
# ==========================================
def call_magisterium_direct(query_text):
    api_key = os.getenv("MAGISTERIUM_API_KEY")
    # 1. Chuẩn hóa URL theo đúng tài liệu
    api_url = os.getenv("MAGISTERIUM_API_URL", "https://www.magisterium.com/api/v1/chat/completions")
    
    if not api_key:
        return {"success": False, "error_message": "❌ Thiếu chìa khóa MAGISTERIUM_API_KEY trong hệ thống."}
        
    headers = {
        "Authorization": f"Bearer {api_key}", 
        "Content-Type": "application/json"
    }
    
    # 2. Chuẩn hóa Payload giống hệt OpenAI/ChatGPT theo tài liệu
    payload = {
        "model": "magisterium-1",
        "messages": [
            {
                "role": "user",
                "content": query_text
            }
        ],
        "stream": False
    }
    
    logger.info(f"🧠 ĐANG GỌI TỚI {api_url} VỚI CÂU HỎI: '{query_text}'...")
    try:
        res = requests.post(api_url, headers=headers, json=payload, timeout=60)
        
        # Xử lý các mã lỗi dựa trên tài liệu
        if res.status_code != 200:
            error_desc = "Lỗi không xác định"
            if res.status_code == 400: error_desc = "Token limit exceeded / Lỗi cú pháp"
            elif res.status_code == 401: error_desc = "Sai API Key hoặc lỗi thanh toán"
            elif res.status_code == 429: error_desc = "Quá nhiều yêu cầu (Rate limit)"
            elif res.status_code >= 500: error_desc = "Lỗi máy chủ Magisterium (Internal server error)"
            
            logger.error(f"❌ MAGISTERIUM TỪ CHỐI! Mã lỗi: {res.status_code} - {res.text}")
            return {"success": False, "error_message": f"❌ Lỗi từ AI: {error_desc}"}
            
        data = res.json()
        
        # 3. Chuẩn hóa cách đọc kết quả (Read response)
        try:
            answer = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            logger.error(f"Lỗi đọc kết quả từ AI: {data}")
            answer = "Có lỗi xảy ra khi đọc dữ liệu từ AI."
            
        return {"success": True, "answer": answer, "citations": data.get("citations", [])}
        
    except requests.exceptions.Timeout:
        return {"success": False, "error_message": "⏱️ AI suy nghĩ quá lâu (Timeout)."}
    except Exception as e:
        logger.error(f"❌ Lỗi mạng: {e}")
        return {"success": False, "error_message": f"❌ Lỗi mạng khi gọi AI: {e}"}

def format_magisterium_response(answer_text, citations):
    answer_clean = answer_text
    # Giới hạn độ dài tránh Zalo block
    if len(answer_clean) > 4000: answer_clean = answer_clean[:3900] + "\n\n[... Xem thêm trên website ...]"
        
    cits_text = ""
    if citations:
        cits_text = "📚 **THAM KHẢO:**\n\n"
        for idx, c in enumerate(citations, 1):
            cits_text += f"[{idx}] {c.get('document_title', 'Tài liệu')}\n"
            if c.get('source_url'): cits_text += f"   🔗 {c.get('source_url')}\n"
            
    return answer_clean, cits_text

@app.route('/webhook/zalo', methods=['POST'])
def receive_webhook():
    data = request.get_json(silent=True) or {}
    payload = data.get("result", data) or {}
    message_obj = payload.get("message", {})
    sender_id = message_obj.get("from", {}).get("id", "")
    message_text = message_obj.get("text", "")

    if sender_id and message_text.startswith("!ask "):
        query = message_text[5:].strip()
        if not query:
            send_zalo_message(sender_id, "❌ Cú pháp: !ask <câu hỏi>")
            return jsonify({"status": "ok"}), 200
            
        def process_ai():
            send_zalo_message(sender_id, "⏳ Magisterium đang xử lý câu hỏi của bạn...")
            res = call_magisterium_direct(query)
            if not res["success"]:
                send_zalo_message(sender_id, res["error_message"])
            else:
                ans, cits = format_magisterium_response(res["answer"], res["citations"])
                send_zalo_message(sender_id, ans)
                if cits: send_zalo_message(sender_id, cits)
                
        threading.Thread(target=process_ai).start()

    return jsonify({"status": "ok"}), 200

@app.route('/', methods=['GET'])
def health(): return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
