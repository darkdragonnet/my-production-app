import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ZALO_API_BASE = "https://bot-api.zaloplatforms.com"

def delete_webhook():
    """Delete webhook"""
    url = f"{ZALO_API_BASE}/bot{BOT_TOKEN}/deleteWebhook"
    
    try:
        response = requests.post(url, json={})
        data = response.json()
        
        print("=" * 60)
        print("DELETE WEBHOOK RESPONSE")
        print("=" * 60)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("=" * 60)
        
        if data.get('ok'):
            print("✅ Webhook deleted successfully!")
        else:
            print(f"❌ Error: {data.get('description')}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    delete_webhook()
