from flask import Flask, request, jsonify
import os
import logging
import requests
import threading

# Import Google GenAI SDK
from google import genai

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("zalo_bot_core")
app = Flask(__name__)

FLASK_API_URL = os.getenv("FLASK_API_URL", "http://zalo-flask-api:5001")

def send_zalo_message(chat_id, text):
    """Gọi ngược lại Flask API cửa trước để trả lời Zalo"""
    try:
        payload = {"chat_id": chat_id, "type": "text", "text": text}
        requests.post(f"{FLASK_API_URL}/send-message", json=payload, timeout=15)
    except Exception as e:
        logger.error(f"❌ Lỗi nhờ Flask API gửi tin: {e}")

# ==========================================
# 🧠 1. MAGISTERIUM AI (Lệnh: !ask)
# ==========================================
def call_magisterium_direct(query_text):
    api_key = os.getenv("MAGISTERIUM_API_KEY")
    api_url = os.getenv("MAGISTERIUM_API_URL", "https://www.magisterium.com/api/v1/chat/completions")
    if not api_key:
        return {"success": False, "error_message": "❌ Thiếu MAGISTERIUM_API_KEY."}

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": "magisterium-1", "messages": [{"role": "user", "content": query_text}], "stream": False}

    try:
        res = requests.post(api_url, headers=headers, json=payload, timeout=60)
        if res.status_code != 200:
            return {"success": False, "error_message": f"❌ Lỗi Magisterium: {res.status_code}"}
        data = res.json()
        return {"success": True, "answer": data["choices"][0]["message"]["content"], "citations": data.get("citations", [])}
    except Exception as e:
        return {"success": False, "error_message": f"❌ Lỗi mạng: {e}"}

def process_magisterium(sender_id, query):
    send_zalo_message(sender_id, "⏳ Magisterium đang tra cứu tài liệu...")
    res = call_magisterium_direct(query)
    if not res["success"]:
        send_zalo_message(sender_id, res["error_message"])
    else:
        answer_clean = res["answer"]
        if len(answer_clean) > 4000: answer_clean = answer_clean[:3900] + "\n\n[...]"
        
        cits_text = ""
        if res["citations"]:
            cits_text = "📚 **THAM KHẢO:**\n" + "\n".join([f"[{i+1}] {c.get('document_title', '')}" for i, c in enumerate(res["citations"])])
            
        send_zalo_message(sender_id, answer_clean)
        if cits_text: send_zalo_message(sender_id, cits_text)

# ==========================================
# 🌟 2. GOOGLE GEMINI (Lệnh: !gemini)
# ==========================================
def process_gemini_ai(sender_id, query):
    try:
        send_zalo_message(sender_id, "⏳ Gemini đang suy nghĩ...")
        client = genai.Client() 
        response = client.models.generate_content(
            model="gemini-3-flash", # Đã fix model có hỗ trợ Free Quota
            contents=query
        )
        answer = response.text
        if len(answer) > 4000: answer = answer[:3900] + "\n\n[...]"
        send_zalo_message(sender_id, answer)
    except Exception as e:
        logger.error(f"❌ Lỗi Gemini AI: {e}")
        send_zalo_message(sender_id, "❌ Lỗi kết nối Gemini.")


# ==========================================
# ⚡ 3. AUTO-REPLY GROQ / NVIDIA (Chat tự do)
# ==========================================
def call_openai_compatible_api(api_url, api_key, model_name, query, extra_headers=None):
    """Hàm lõi dùng chung để gọi API chuẩn OpenAI (Groq, NVIDIA, OpenRouter)"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    if extra_headers:
        headers.update(extra_headers)
        
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": query}],
        "stream": False,
        "max_tokens": 1500
    }
    
    res = requests.post(api_url, headers=headers, json=payload, timeout=45)
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]


def process_smart_reply(sender_id, query):
    """Worker Thread: Xử lý chat tự do có Fallback"""
    send_zalo_message(sender_id, "⏳ Bot đang suy nghĩ...")
    answer = ""
    
    groq_key = os.getenv("GROQ_API_KEY")
    nv_key = os.getenv("NVIDIA_API_KEY")

    # --- BƯỚC 1: THỬ GROQ TRƯỚC ---
    if groq_key:
        try:
            logger.info("⚡ Đang gọi Groq (Llama 3.3 Versatile)...")
            answer = call_openai_compatible_api(
                api_url="https://api.groq.com/openai/v1/chat/completions",
                api_key=groq_key,
                model_name="llama-3.3-70b-versatile",
                query=query
            )
        except Exception as e:
            logger.warning(f"⚠️ Groq gọi API lỗi: {e}. Đang chuyển hướng...")
    else:
        logger.warning("⚠️ BỎ QUA GROQ: Không tìm thấy GROQ_API_KEY")

    # --- BƯỚC 2: DỰ PHÒNG NVIDIA API ---
    if not answer:
        if nv_key:
            try:
                logger.info("🔄 Đang định tuyến vào NVIDIA API (Llama 3.3 70B)...")
                answer = call_openai_compatible_api(
                    api_url="https://integrate.api.nvidia.com/v1/chat/completions",
                    api_key=nv_key,
                    model_name="meta/llama-3.3-70b-instruct",
                    query=query
                )
            except Exception as e:
                logger.error(f"❌ NVIDIA API lỗi: {e}")
        else:
            logger.warning("⚠️ BỎ QUA NVIDIA: Không tìm thấy NVIDIA_API_KEY")

    # --- BƯỚC 3: XỬ LÝ KẾT QUẢ ---
    if answer:
        if len(answer) > 4000: answer = answer[:3900] + "\n\n[... Chiều dài vượt quá giới hạn ...]"
        send_zalo_message(sender_id, answer)
        logger.info(f"✅ Đã Auto-Reply thành công cho user {sender_id}")
    else:
        send_zalo_message(sender_id, "❌ Bot hiện đang quá tải hoặc lỗi cấu hình API.")
        logger.error("❌ Thread Auto-reply kết thúc: Không có câu trả lời.")


# ==========================================
# 🎯 4. GỌI ĐÍCH DANH MODEL QUA NVIDIA API
# ==========================================
def process_nvidia_ai(sender_id, query):
    """Worker Thread: Xử lý lệnh gọi !llama qua máy chủ NVIDIA"""
    send_zalo_message(sender_id, "⏳ NVIDIA Llama 3.3 đang phân tích yêu cầu...")
    
    try:
        nv_key = os.getenv("NVIDIA_API_KEY")
        if not nv_key:
            send_zalo_message(sender_id, f"❌ Hệ thống thiếu NVIDIA_API_KEY trong .env.")
            return

        # Gọi qua hàm lõi có sẵn, chỉ đổi URL và cấu hình
        answer = call_openai_compatible_api(
            api_url="https://integrate.api.nvidia.com/v1/chat/completions",
            api_key=nv_key,
            model_name="meta/llama-3.3-70b-instruct",
            query=query
        )
        
        if answer:
            if len(answer) > 4000: 
                answer = answer[:3900] + "\n\n[... Chiều dài vượt quá giới hạn ...]"
            send_zalo_message(sender_id, answer)
            logger.info(f"✅ Đã trả lời bằng NVIDIA Llama thành công.")
            
    except Exception as e:
        logger.error(f"❌ Lỗi khi gọi NVIDIA API: {e}", exc_info=True)
        send_zalo_message(sender_id, f"❌ Máy chủ NVIDIA hiện đang bận hoặc gặp sự cố.")

# ==========================================
# 🚪 BỘ ĐỊNH TUYẾN WEBHOOK (ROUTER)
# ==========================================
@app.route('/webhook/zalo', methods=['POST'])
def receive_webhook():
    data = request.get_json(silent=True) or {}
    payload = data.get("result", data) or {}
    message_obj = payload.get("message", {})
    sender_id = message_obj.get("from", {}).get("id", "")
    message_text = message_obj.get("text", "")

    if sender_id and message_text:
        
        # LUỒNG 1: Lệnh !ask -> Magisterium
        if message_text.startswith("!ask "):
            query = message_text[5:].strip()
            if query: threading.Thread(target=process_magisterium, args=(sender_id, query), daemon=True).start()
            
        # LUỒNG 2: Lệnh !gemini -> Google Gemini
        elif message_text.startswith("!gemini "):
            query = message_text[8:].strip()
            if query: threading.Thread(target=process_gemini_ai, args=(sender_id, query), daemon=True).start()
            
        # LUỒNG 3: Lệnh !llama -> NVIDIA Llama 3.3 70B
        elif message_text.startswith("!llama "):
            query = message_text[7:].strip()
            if query:
                threading.Thread(target=process_nvidia_ai, args=(sender_id, query), daemon=True).start()
                
        # LUỒNG 4: Chat tự nhiên -> Tự động dùng Groq (allam-2-7b), lỗi thì qua NVIDIA
        else:
            threading.Thread(target=process_smart_reply, args=(sender_id, message_text), daemon=True).start()

    return jsonify({"status": "ok"}), 200

@app.route('/', methods=['GET'])
def health(): 
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
