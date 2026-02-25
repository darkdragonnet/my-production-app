import os
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*70)
print("🔐 ZALO BOT CONFIGURATION")
print("="*70)

print("\n📱 BOT CREDENTIALS:")
print(f"  • BOT_ID: {os.getenv('BOT_ID', 'NOT SET')}")
print(f"  • SECRET_KEY: {os.getenv('SECRET_KEY', 'NOT SET')}")
print(f"  • ACCESS_TOKEN: {os.getenv('ACCESS_TOKEN', 'NOT SET')}")

print("\n🌐 WEBHOOK CONFIGURATION:")
print(f"  • WEBHOOK_URL: {os.getenv('WEBHOOK_URL', 'NOT SET')}")
print(f"  • WEBHOOK_SECRET: {os.getenv('WEBHOOK_SECRET', 'NOT SET')}")

print("\n🔗 API ENDPOINTS:")
print(f"  • Flask Server: http://127.0.0.1:5002")
print(f"  • Dashboard: http://127.0.0.1:5003")
print(f"  • Auto-Reply Bot: Running")

print("\n📊 ENVIRONMENT VARIABLES:")
for key, value in os.environ.items():
    if any(x in key.upper() for x in ['ZALO', 'BOT', 'SECRET', 'TOKEN', 'WEBHOOK']):
        masked_value = value[:10] + "..." if len(str(value)) > 10 else value
        print(f"  • {key}: {masked_value}")

print("\n" + "="*70 + "\n")

