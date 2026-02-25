from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    """Dashboard homepage"""
    return render_template('dashboard.html')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics from Flask Server"""
    try:
        # Lấy messages từ Flask Server (port 5001)
        response = requests.get('http://localhost:5001/api/messages', timeout=5)

        if response.status_code == 200:
            data = response.json()
            messages = data.get('messages', [])

            # Tính toán stats
            unique_users = len(set(m['sender_id'] for m in messages))

            return jsonify({
                'total_messages': len(messages),
                'total_users': unique_users,
                'messages': messages[-20:]  # 20 messages gần nhất
            }), 200
        else:
            return jsonify({
                'total_messages': 0,
                'total_users': 0,
                'messages': [],
                'error': f'Flask Server error: {response.status_code}'
            }), 200

    except requests.exceptions.ConnectionError:
        return jsonify({
            'total_messages': 0,
            'total_users': 0,
            'messages': [],
            'error': 'Cannot connect to Flask Server (http://localhost:5001)'
        }), 200
    except Exception as e:
        print(f"Error in get_stats: {str(e)}")
        return jsonify({
            'total_messages': 0,
            'total_users': 0,
            'messages': [],
            'error': str(e)
        }), 200

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'service': 'Dashboard',
        'port': 5004,
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5004))
    print("\n" + "="*60)
    print("📊 ZALO BOT DASHBOARD")
    print("="*60)
    print(f"Open http://localhost:{port} in your browser")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=port, debug=False)
