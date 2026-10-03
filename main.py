import os
import requests
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

# WhatsApp API Key load karein
WHATSAPP_API_KEY = os.environ.get("WHATSAPP_API_TOKEN")

# All 9 Gemini API Keys ko list me load karein
GEMINI_KEYS = [
    os.environ.get(f"GEMINI_KEY_{i}") for i in range(1, 10)
]
# Empty/None keys ko remove karein
GEMINI_KEYS = [key for key in GEMINI_KEYS if key]

def ask_gemini(user_message):
    """
    Sabhi 9 keys me se ek-ek karke try karega.
    Agar pehli key limit cross kare, toh automatic agli key use hogi.
    """
    for index, key in enumerate(GEMINI_KEYS):
        try:
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_message,
            )
            print(f"Success using Gemini Key #{index + 1}")
            return response.text
        except Exception as e:
            print(f"Gemini Key #{index + 1} failed or limit exceeded: {e}")
            continue

    return "Sorry, sabhi Gemini API keys ki daily limit exhaust ho chuki hai."

def send_whatsapp_message(to_number, message_text):
    """WhatsApp API Key ka use karke user ko reply bhejta hai"""
    url = "https://graph.facebook.com/v18.0/YOUR_AGENT_ID/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message_text}
    }
    try:
        res = requests.post(url, headers=headers, json=payload)
        return res.json()
    except Exception as e:
        print(f"WhatsApp Send Error: {e}")
        return None

@app.route('/', methods=['GET'])
def home():
    return f"WhatsApp Gemini Bot is live with {len(GEMINI_KEYS)} Gemini backup keys!", 200

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    try:
        data = request.get_json()
        print("Incoming Data:", data)

        # Incoming data se user msg aur phone number extract karein
        # (Apne webhook payload ke structure ke mutabiq adjust karein)
        user_msg = data.get('message', '') if data else ''
        sender_phone = data.get('from', '') if data else ''

        if user_msg:
            # 1. 9 Keys rotation se Gemini ka response lein
            gemini_reply = ask_gemini(user_msg)
            # 2. Response ko WhatsApp API key se user ko bhej dein
            if sender_phone:
                send_whatsapp_message(sender_phone, gemini_reply)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"Webhook Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
