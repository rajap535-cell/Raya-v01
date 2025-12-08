from flask import Flask, request
import requests  # You missed importing this earlier

app = Flask(__name__)

VERIFY_TOKEN = 'rayalite_verify'
WHATSAPP_TOKEN = 'EAASAvYrwZAQsBPAyeUUCYPmyWMYe3QFHnhTKHANUeBSWLZAF5xxiUdtZA2TwCMhB9FVazHK973nDy5jult88Uf2e9IUyCUXZCW2oRMhPKYgMDpdZBdVJSayM0ZBSnvHKw42JAwHvHwCfNMYnmToVZBxteXrfSms1b6MzUpaNZAHDkcKcZAKGFMQPagxMZCBZAQlNFDvPGnmn0QdYYcZAsSUdayeu31fcHQfXBH8YPU643QZDZD'

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print('WEBHOOK_VERIFIED')
            return challenge, 200
        else:
            return 'Verification token mismatch', 403

    if request.method == 'POST':
        data = request.get_json()
        print("Received POST request:", data)  # Debug incoming payload

        if data and 'entry' in data:
            for entry in data['entry']:
                for change in entry.get('changes', []):
                    value = change.get('value')
                    messages = value.get('messages')
        if 'messages' in value:
            message = value['messages'][0]
            phone_number_id = value['metadata']['phone_number_id']
            from_number = message['from']
            text = message['text']['body']

    print("Incoming message from:", from_number)
    print("Message text:", text)
    print("Phone Number ID:", phone_number_id)
    print("Sending reply...")

    reply_message = f"Hello! R.A.Y.A here. You said: {text}"  # <-- Dynamic reply!

    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    headers = {
        'Authorization': f'Bearer {WHATSAPP_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        'messaging_product': 'whatsapp',
        'to': from_number,
        'type': 'text',
        'text': {'body': reply_message}
    }

    response = requests.post(url, headers=headers, json=payload)
    print("API Response Status Code:", response.status_code)
    print("API Response Body:", response.text)

    return 'EVENT_RECEIVED', 200

if __name__ == '__main__':
    app.run(port=5000)
