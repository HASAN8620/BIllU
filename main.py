from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Render ke Environment Variables se Key/Token load karein
API_TOKEN = os.environ.get("WHATSAPP_API_TOKEN")

@app.route('/', methods=['GET'])
def home():
    return "WhatsApp Bot Server is live and running on Render!", 200

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """
    Agar aap Meta/WhatsApp Cloud API ka Webhook Verification use kar rahe hain.
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "my_secret_verify_token")

    if mode and token:
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            return "Forbidden", 403
    return "Webhook Verification Endpoint", 200

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """
    Jab bhi WhatsApp par koi message aayega, yeh function response karega.
    """
    try:
        data = request.get_json()
        print("Incoming Webhook Data:", data)

        # Aapka message processing logic yahan aayega
        # Example: Incoming message check karna
        if data:
            # Apne requirement ke mutabiq logic add karein
            pass

        return jsonify({"status": "success", "message": "Event received"}), 200

    except Exception as e:
        print(f"Error handling webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Render automatically PORT environment variable provide karta hai
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
      
