from flask import Flask, request, jsonify
import threading
from Main import run_automation

app = Flask(__name__)

@app.route('/trigger', methods=['POST'])
def trigger_bot():
    data = request.json
    thread = threading.Thread(target=run_automation, args=(data,))
    thread.start()
    return jsonify({"status": "Automation started"}), 202

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
