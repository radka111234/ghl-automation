from flask import Flask, request, jsonify
import threading
from Main import run_automation

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "✅ GHL Automation is live", 200

@app.route('/trigger', methods=['POST'])
def trigger_bot():
    print("📬 Received /trigger request")
    data = request.get_json()
    print("📦 Payload:", data)
    thread = threading.Thread(target=run_automation, args=(data,))
    thread.start()
    return jsonify({"status": "Automation started"}), 202


import os

if __name__ == '__main__':
    try:
        port = int(os.environ.get("PORT", 10000))
        print(f"🟢 Starting Flask app on port {port}")
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        print(f"❌ Failed to start Flask app: {e}")
