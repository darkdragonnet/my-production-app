from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Flask API is running!"
    }), 200

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({
        "message": "Hello from Production!"
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)
