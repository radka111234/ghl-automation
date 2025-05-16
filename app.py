from flask import Flask, request, jsonify
import subprocess
import json
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'HEAD'])
def health_check():
    return "✅ GHL Automation is live", 200

@app.route('/trigger', methods=['GET', 'POST', 'HEAD'])
def run_bot():

    if request.method in ['GET', 'HEAD']:
        return "✅ GHL Automation is live", 200

    try:
        data = request.get_json()
        print("📥 Incoming request with data:", data, flush=True)
        required_fields = ['client_name', 'lead_name', 'email', 'business_name']
        print("📥 Incoming request with data:", data)

        if not all(field in data for field in required_fields):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        # Run the bot and capture output
        print("🔥 Starting subprocess with:", json.dumps(data), flush=True)

        result = subprocess.run(
            ["python3", "Main.py", json.dumps(data)],
            capture_output=True,
            text=True
        )

        print("📤 Subprocess STDOUT:\n", result.stdout, flush=True)
        print("📥 Subprocess STDERR:\n", result.stderr, flush=True)



        if result.returncode != 0:
            return jsonify({"status": "error", "message": result.stderr}), 500

        return jsonify({"status": "success", "message": result.stdout.strip()}), 200

    except Exception as e:
        print("❌ Flask caught exception:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    try:
        port = int(os.environ.get("PORT", 10000))
        print(f"🟢 Starting Flask app on port {port}")
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        print(f"❌ Failed to start Flask app: {e}")
