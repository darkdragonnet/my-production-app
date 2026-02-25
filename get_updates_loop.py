import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ZALO_API_BASE = "https://bot-api.zaloplatforms.com"

def get_updates():
    """Get updates from Zalo Bot API"""
    url = f"{ZALO_API_BASE}/bot{BOT_TOKEN}/getUpdates"
    
    try:
        response = requests.post(url, json={"timeout": 30})
        data = response.json()
        
        # Chỉ in nếu có tin nhắn
        if data.get('ok') and data.get('result'):
            print("\n" + "=" * 60)
            print("📨 NEW MESSAGE RECEIVED!")
            print("=" * 60)
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("=" * 60)
            
            # Extract info from message
            result = data.get('result', {})
            message = result.get('message', {})
            
            if message:
                chat = message.get('chat', {})
                sender = message.get('from', {})
                
                chat_id = chat.get('id') or sender.get('id')
                sender_name = sender.get('display_name', 'Unknown')
                text = message.get('text', '')
                
                print(f"\n✅ Chat ID: {chat_id}")
                print(f"👤 Sender: {sender_name}")
                print(f"📝 Message: {text}")
        else:
            # In dấu chấm để chỉ ra đang chờ
            print(".", end="", flush=True)
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

def main():
    print("\n" + "=" * 60)
    print("🤖 ZALO BOT - WAITING FOR MESSAGES")
    print("=" * 60)
    print("Waiting for messages... (Press Ctrl+C to stop)")
    print("Hint: Send a message to the bot from Zalo\n")
    
    try:
        while True:
            get_updates()
            time.sleep(1)  # Chờ 1 giây trước khi poll lại
    
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped!")

if __name__ == '__main__':
    main()
