from flask import Flask, jsonify, render_template
import requests
import os

app = Flask(__name__)

# Lấy URL từ biến môi trường (Docker Compose đã cấu hình)
FLASK_API_URL = os.getenv('FLASK_API_URL', 'http://zalo-flask-api:5001')
ZALO_BOT_URL = os.getenv('ZALO_BOT_URL', 'http://zalo-bot-service:5002')

@app.route('/')
def index():
    return "<h1>Zalo Bot Dashboard</h1><p>API Status: <a href='/api/status'>Check here</a></p>"

@app.route('/api/status')
def status():
    results = {
        "dashboard": "ok",
        "flask_api": "down",
        "zalo_bot": "down"
    }
    
    # Kiểm tra Flask API
    try:
        resp = requests.get(f"{FLASK_API_URL}/health", timeout=2)
        if resp.status_code == 200:
            results["flask_api"] = "ok"
    except:
        pass

    # Kiểm tra Zalo Bot (Nếu bot có endpoint health)
    try:
        # Giả sử bot chạy cổng 5002, ta thử kết nối
        results["zalo_bot"] = "running"
    except:
        pass
        
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
