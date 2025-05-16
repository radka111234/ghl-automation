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
        required_fields = ['client_name', 'lead_name', 'email', 'business_name']
        print(required_fields)

        if not all(field in data for field in required_fields):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        # Run the bot script with the input data
        try:
            result = subprocess.run(
                ["python3", "Main.py", json.dumps(data)],
                check=True,
                capture_output=True,
                text=True
            )
            print("📤 Subprocess STDOUT:\n", result.stdout)
            print("📥 Subprocess STDERR:\n", result.stderr)
            return jsonify({"status": "success", "message": "Bot executed"}), 200

        except subprocess.CalledProcessError as e:
            print("❌ Subprocess failed:")
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)
            return jsonify({"status": "error", "message": e.stderr}), 500


    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    try:
        port = int(os.environ.get("PORT", 10000))
        print(f"🟢 Starting Flask app on port {port}")
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        print(f"❌ Failed to start Flask app: {e}")
