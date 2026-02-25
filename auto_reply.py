import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ZALO_API_BASE = "https://bot-api.zaloplatforms.com"
DASHBOARD_URL = "http://127.0.0.1:5004"

# Track processed messages
processed_messages = set()

def get_updates():
    """Get updates from Zalo Bot API"""
    url = f"{ZALO_API_BASE}/bot{BOT_TOKEN}/getUpdates"
    
    try:
        response = requests.post(url, json={"timeout": 30})
        return response.json()
    except Exception as e:
        print(f"❌ Error getting updates: {str(e)}")
        return None

def send_message(chat_id, text):
    """Send message to user"""
    url = f"{ZALO_API_BASE}/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        
        if data.get('ok'):
            print(f"✅ Sent message to {chat_id}: {text[:50]}...")
            return True
        else:
            print(f"❌ Failed to send message: {data}")
            return False
    except Exception as e:
        print(f"❌ Error sending message: {str(e)}")
        return False

def send_chat_action(chat_id, action='typing'):
    """Send chat action (typing indicator)"""
    url = f"{ZALO_API_BASE}/bot{BOT_TOKEN}/sendChatAction"
    payload = {
        "chat_id": chat_id,
        "action": action
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        
        if data.get('ok'):
            return True
        else:
            return False
    except Exception as e:
        return False

def log_to_dashboard(sender_id, sender_name, text):
    """Log message to dashboard"""
    try:
        url = f"{DASHBOARD_URL}/api/message/log"
        payload = {
            "sender_id": sender_id,
            "sender_name": sender_name,
            "text": text
        }
        print(f"📤 Logging to dashboard: {sender_name} - {text[:30]}...")
        response = requests.post(url, json=payload, timeout=2)
        result = response.json()
        if result.get('ok'):
            print(f"✅ Logged to dashboard successfully")
        return result.get('ok', False)
    except Exception as e:
        print(f"⚠️ Failed to log to dashboard: {str(e)}")
        return False

def process_message(update):
    """Process incoming message"""
    try:
        result = update.get('result', {})
        message = result.get('message', {})
        
        if not message:
            return
        
        chat = message.get('chat', {})
        sender = message.get('from', {})
        
        chat_id = chat.get('id') or sender.get('id')
        sender_name = sender.get('display_name', 'Unknown')
        message_id = message.get('message_id')
        text = message.get('text', '')
        
        # Avoid processing same message twice
        if message_id in processed_messages:
            return
        
        processed_messages.add(message_id)
        
        print(f"\n📨 New message from {sender_name} ({chat_id}):")
        print(f"   Text: {text}")
        
        # Log to dashboard FIRST
        log_to_dashboard(chat_id, sender_name, text)
        
        # Show typing indicator
        send_chat_action(chat_id, 'typing')
        
        # Wait a bit to simulate processing
        time.sleep(1)
        
        # Generate response
        response_text = generate_response(text, sender_name)
        
        # Send response
        send_message(chat_id, response_text)
        
    except Exception as e:
        print(f"❌ Error processing message: {str(e)}")

def generate_response(user_message, sender_name):
    """Generate response based on user message"""
    user_message = user_message.lower().strip()
    
    # Simple keyword matching
    if 'hello' in user_message or 'hi' in user_message or 'xin chào' in user_message:
        return f"👋 Xin chào {sender_name}! Mình là bot. Có gì mình giúp bạn không?"
    
    elif 'help' in user_message or 'trợ giúp' in user_message:
        return """🆘 Mình có thể giúp bạn:
1️⃣ Trả lời câu hỏi
2️⃣ Gửi thông tin
3️⃣ Hỗ trợ khách hàng

Hãy nhập lệnh hoặc câu hỏi của bạn!"""
    
    elif 'thanks' in user_message or 'cảm ơn' in user_message or 'thank' in user_message:
        return "😊 Không có gì! Hẹn gặp lại bạn!"
    
    elif 'bye' in user_message or 'tạm biệt' in user_message or 'goodbye' in user_message:
        return "👋 Tạm biệt! Hẹn gặp lại bạn lần sau!"
    
    else:
        return f"📝 Bạn vừa nói: \"{user_message}\"\n\nMình hiện chưa hiểu. Hãy thử lệnh 'help' để xem hướng dẫn!"

def main():
    """Main loop"""
    print("\n" + "=" * 60)
    print("🤖 Zalo Bot Auto-Reply Started!")
    print("=" * 60)
    print("Waiting for messages... (Press Ctrl+C to stop)")
    print("=" * 60 + "\n")
    
    try:
        while True:
            # Get updates
            data = get_updates()
            
            if data and data.get('ok'):
                result = data.get('result', {})
                
                if result and result.get('message'):
                    print(f"\n📬 Received update")
                    process_message(data)
                
                # Wait before next poll
                time.sleep(2)
            else:
                print(".", end="", flush=True)
                time.sleep(5)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped!")
    except Exception as e:
        print(f"❌ Error in main loop: {str(e)}")

if __name__ == '__main__':
    main()
