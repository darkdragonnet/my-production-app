import os
import requests
import json
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
        
        print("=" * 60)
        print("ZALO BOT UPDATES")
        print("=" * 60)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("=" * 60)
        
        # Extract chat_id from updates
        if data.get('ok') and data.get('result'):
            for update in data.get('result', []):
                if 'sender' in update:
                    chat_id = update['sender'].get('id')
                    print(f"\n✅ Chat ID: {chat_id}")
                    
                    if 'message' in update:
                        message = update['message']
                        if 'text' in message:
                            print(f"📝 Message: {message['text']}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    get_updates()
