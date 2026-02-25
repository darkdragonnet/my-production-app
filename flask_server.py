from flask import Flask, request, jsonify
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Store messages in memory (for demo)
messages = []

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': 'Flask Bot Server'
    }), 200

@app.route('/api/message/log', methods=['POST'])
def log_message():
    """Log message from bot"""
    try:
        data = request.get_json()
        
        message = {
            'sender_id': data.get('sender_id'),
            'sender_name': data.get('sender_name'),
            'text': data.get('text'),
            'timestamp': datetime.now().isoformat()
        }
        
        messages.append(message)
        
        return jsonify({'ok': True, 'message': 'Logged successfully'}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Get all logged messages"""
    return jsonify({
        'messages': messages,
        'count': len(messages)
    }), 200

@app.route('/api/messages/<sender_id>', methods=['GET'])
def get_user_messages(sender_id):
    """Get messages from specific user"""
    user_messages = [m for m in messages if m['sender_id'] == sender_id]
    return jsonify({
        'messages': user_messages,
        'count': len(user_messages)
    }), 200

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔌 FLASK BOT SERVER")
    print("="*60)
    print("Running on http://127.0.0.1:5002")
    print("="*60 + "\n")
    
    app.run(host='127.0.0.1', port=5001, debug=False)
