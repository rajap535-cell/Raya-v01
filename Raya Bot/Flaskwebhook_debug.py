# Final merged webhook: copy-paste ready (replace tokens/URIs)
from flask import Flask, request
import requests, json, os, io, datetime
from pymongo import MongoClient
import PyPDF2
import re
from heapq import nlargest

app = Flask(__name__)

# ---------------- CONFIG ----------------
VERIFY_TOKEN = 'rayalite_verify'  # keep your verify token
WHATSAPP_TOKEN = 'EAASAvYrwZAQsBPI4KKzZCEY1iYWqYvEfHtlMaTOerHBUi7D0dFYqwJiRpxbqULmtz6HJZBnhGmkdw8MSGUiuSvArinlSt43llSe9y5kaML5fUBmts6XV7qM08woMHZBvd9hyt44Bd6kyK3v6LMgPxa2XOZCpJvwCXClYAwp2g4bYJgjCU3p3rO34VT0bKN'  # REPLACE: e.g. EAAX...
MONGO_URI = "mongodb+srv://rajap535:vO7uZtx4A9TVoMeE@cluster0.vnfaxqc.mongodb.net/?"  # REPLACE: mongodb+srv://...

# ---------------- DB ----------------
client = MongoClient(MONGO_URI)
db = client.get_database('Raya_database')
user_interactions = db.get_collection('user_interactions')
conversation = db.get_collection('conversation')
farmer_images = db.get_collection('farmer_images')

# ---------------- STATE ----------------
processed_messages = set()   # message_id dedupe
user_state = {}              # per-user state, e.g. {phone: {"mode":"main"/"farmer","step":"awaiting_crop_image"}}

# ---------------- HELPERS ----------------
def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

def log_interaction(user_id, user_message, raya_response, extra=None):
    doc = {
        'user_id': user_id,
        'user_message': user_message,
        'raya_response': raya_response,
        'ts': utc_now()
    }
    if extra:
        doc.update(extra)
    try:
        user_interactions.insert_one(doc)
    except Exception as e:
        print("Mongo log error:", e)

def fetch_joke():
    try:
        r = requests.get("https://official-joke-api.appspot.com/jokes/random", timeout=6)
        if r.status_code == 200:
            j = r.json()
            return f"{j.get('setup','')} ... {j.get('punchline','')}"
    except Exception as e:
        print("joke fetch error:", e)
    return "Oops! Couldn't fetch a joke right now. Try again later."

def extract_summary(text, max_sentences=5):
    if not text:
        return ""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    word_freq = {}
    for w in re.findall(r'\w+', text.lower()):
        if len(w) > 3:
            word_freq[w] = word_freq.get(w, 0) + 1
    sentence_scores = {}
    for s in sentences:
        score = 0
        for w in re.findall(r'\w+', s.lower()):
            score += word_freq.get(w, 0)
        sentence_scores[s] = score
    best = nlargest(min(max_sentences, len(sentences)), sentence_scores, key=sentence_scores.get)
    return " ".join(best).strip()

def veda_ai_summary(text):
    return f"[V.E.D.A] (placeholder summary) — {min(300, len(text))} chars processed."

def send_whatsapp_message(to, body, phone_number_id):
    """
    Uses the WhatsApp Cloud API send endpoint.
    phone_number_id must be provided (from incoming webhook metadata).
    """
    if not WHATSAPP_TOKEN or WHATSAPP_TOKEN.startswith("YOUR_"):
        print("Warning: WHATSAPP_TOKEN not set or placeholder.")
    if not phone_number_id:
        print("Warning: phone_number_id missing, cannot send.")
        return None

    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    headers = {
        'Authorization': f'Bearer {WHATSAPP_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        'messaging_product': 'whatsapp',
        'to': to,
        'type': 'text',
        'text': {'body': body}
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        print("Send API:", r.status_code, r.text)
        return r
    except Exception as e:
        print("Error sending WhatsApp message:", e)
        return None

# ---------------- FARMER PLACEHOLDERS ----------------
def farmer_crop_disease_detection(image_url):
    # placeholder result - replace with ML service call
    return "🌾 Crop Detection (mock): Early Blight suspected. Suggested: Neem oil spray."

def farmer_weather_irrigation(area):
    return f"🌦 Weather for {area}: 30–32°C, light rain possible. Irrigation: light watering tomorrow."

def farmer_market_price_predictor(crop):
    return f"📈 Market (mock) {crop}: ₹2200/quintal in nearest mandi. Suggest: sell within 3 days."

def farmer_voice_assistant(query):
    return f"🗣️ Voice assistant (mock): You asked '{query}'. Reply: Follow local extension advice."

def farmer_fertilizer_optimizer(crop, soil):
    return f"🧪 Fertilizer suggestion (mock) for {crop} on {soil}: 50kg Urea / ha + 20kg DAP / ha (example)."

# ---------------- MENUS ----------------
MAIN_MENU = (
    "Hi! I'm R.A.Y.A 🤖✨\n"
    "I can assist you with:\n"
    "1️⃣ Weather Updates\n"
    "2️⃣ Daily Motivation\n"
    "3️⃣ News Headlines\n"
    "4️⃣ Document Summaries\n"
    "Type 'farmer' for Farmer AI features or 'joke' for a joke."
)

FARMER_MENU = (
    "👨‍🌾 Farmer AI Menu:\n"
    "1️⃣ Crop Disease Detection\n"
    "2️⃣ Weather & Irrigation Advice\n"
    "3️⃣ Market Price Prediction\n"
    "4️⃣ Voice Assistant (Local Language)\n"
    "5️⃣ Fertilizer Optimization\n"
    "Type 'exit' to return to main menu."
)

# ---------------- WEBHOOK ----------------
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # GET: verification (Meta)
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print('WEBHOOK_VERIFIED')
            return challenge, 200
        return 'Verification token mismatch', 403

    # POST: incoming messages
    data = request.get_json(silent=True)
    print("Received POST:", json.dumps(data, indent=2) if data else "No JSON")

    if not data:
        return "EVENT_RECEIVED", 200

    # Only proceed for WhatsApp business events
    if data.get('object') != 'whatsapp_business_account':
        return "EVENT_RECEIVED", 200

    for entry in data.get('entry', []):
        for change in entry.get('changes', []):
            value = change.get('value', {})
            metadata = value.get('metadata', {}) or {}
            phone_number_id = metadata.get('phone_number_id')  # used for sending replies
            contacts = value.get('contacts', []) or []
            messages = value.get('messages', []) or []

            # if no messages, skip
            if not messages:
                continue

            for msg in messages:
                message_id = msg.get('id')
                if not message_id:
                    continue

                # Dedupe - if we've processed this message_id, skip
                if message_id in processed_messages:
                    print("Duplicate message, skipping:", message_id)
                    continue
                processed_messages.add(message_id)

                # identify sender
                from_number = msg.get('from')  # e.g. "917xxxxxxxxx"
                if not from_number:
                    continue

                # ensure user state exists
                if from_number not in user_state:
                    user_state[from_number] = {'mode': 'main', 'step': 'main'}

                current_mode = user_state[from_number]['mode']
                current_step = user_state[from_number]['step']
                msg_type = msg.get('type')

                # ---------- TEXT ----------
                if msg_type == 'text':
                    text = (msg.get('text') or {}).get('body', '').strip()
                    text_l = text.lower()

                    # quick intents
                    if text_l in ['hi', 'hello', 'hey', 'menu']:
                        user_state[from_number] = {'mode': 'main', 'step': 'main'}
                        send_whatsapp_message(from_number, MAIN_MENU, phone_number_id)
                        log_interaction(from_number, text, MAIN_MENU, extra={'mode':'main'})
                        continue

                    if 'joke' in text_l:
                        joke = fetch_joke()
                        send_whatsapp_message(from_number, joke, phone_number_id)
                        log_interaction(from_number, text, joke, extra={'intent':'joke'})
                        continue

                    if 'farmer' in text_l or 'kisan' in text_l:
                        user_state[from_number] = {'mode': 'farmer', 'step': 'main'}
                        send_whatsapp_message(from_number, FARMER_MENU, phone_number_id)
                        log_interaction(from_number, text, FARMER_MENU, extra={'mode':'farmer'})
                        continue

                    # If user in farmer mode
                    if current_mode == 'farmer':
                        # awaiting sub-step or selection
                        if current_step == 'awaiting_crop_image':
                            # user sent text but we expect an image
                            send_whatsapp_message(from_number, "Please send an image of the leaf (use the paperclip -> Photo).", phone_number_id)
                            log_interaction(from_number, text, "asked for image", extra={'mode':'farmer','step':current_step})
                            continue

                        # handle farmer menu selection
                        if text_l in ['1','2','3','4','5']:
                            if text_l == '1':
                                user_state[from_number]['step'] = 'awaiting_crop_image'
                                send_whatsapp_message(from_number, "Please send me a clear image of the affected crop leaf (as an image file).", phone_number_id)
                                log_interaction(from_number, text, "awaiting crop image", extra={'mode':'farmer'})
                                continue
                            elif text_l == '2':
                                res = farmer_weather_irrigation("your area")
                                send_whatsapp_message(from_number, res, phone_number_id)
                                log_interaction(from_number, text, res, extra={'mode':'farmer'})
                                continue
                            elif text_l == '3':
                                res = farmer_market_price_predictor("wheat")
                                send_whatsapp_message(from_number, res, phone_number_id)
                                log_interaction(from_number, text, res, extra={'mode':'farmer'})
                                continue
                            elif text_l == '4':
                                res = farmer_voice_assistant("sample query")
                                send_whatsapp_message(from_number, res, phone_number_id)
                                log_interaction(from_number, text, res, extra={'mode':'farmer'})
                                continue
                            elif text_l == '5':
                                res = farmer_fertilizer_optimizer("rice","clay")
                                send_whatsapp_message(from_number, res, phone_number_id)
                                log_interaction(from_number, text, res, extra={'mode':'farmer'})
                                continue
                        # allow exit/back
                        if text_l in ['exit','back','quit','menu']:
                            user_state[from_number] = {'mode':'main','step':'main'}
                            send_whatsapp_message(from_number, "Exited Farmer Mode.\n" + MAIN_MENU, phone_number_id)
                            log_interaction(from_number, text, "exited farmer mode", extra={'mode':'main'})
                            continue

                        # invalid option in farmer mode
                        send_whatsapp_message(from_number, "Invalid option in Farmer Menu. Type 1-5 or 'exit'.", phone_number_id)
                        log_interaction(from_number, text, "invalid farmer option", extra={'mode':'farmer'})
                        continue

                    # Not in farmer mode -> main menu options
                    # e.g., 1 weather, 2 motivation, 3 news, 4 pdf summary
                    if text_l == '1':
                        w = "Today's weather: Sunny 32°C (mock)."
                        send_whatsapp_message(from_number, w, phone_number_id)
                        log_interaction(from_number, text, w, extra={'mode':'main'})
                        continue
                    if text_l == '2':
                        m = "Motivation: Push yourself, because no one else is going to do it for you."
                        send_whatsapp_message(from_number, m, phone_number_id)
                        log_interaction(from_number, text, m, extra={'mode':'main'})
                        continue
                    if text_l == '3':
                        n = "Top News (mock): India's space program advancing."
                        send_whatsapp_message(from_number, n, phone_number_id)
                        log_interaction(from_number, text, n, extra={'mode':'main'})
                        continue
                    if text_l == '4':
                        send_whatsapp_message(from_number, "Please send a PDF document you want summarized.", phone_number_id)
                        log_interaction(from_number, text, "requested pdf", extra={'mode':'main'})
                        continue

                    # fallback
                    send_whatsapp_message(from_number, "I didn't understand that. Type 'Hi' for menu or 'farmer' for agriculture tools.", phone_number_id)
                    log_interaction(from_number, text, "fallback", extra={'mode':current_mode})
                    continue

                # ---------- IMAGE ----------
                if msg_type == 'image':
                    # get media id then URL via Graph API
                    image = msg.get('image', {}) or {}
                    media_id = image.get('id')
                    if not media_id:
                        send_whatsapp_message(from_number, "No media id found, try sending image again.", phone_number_id)
                        continue
                    # fetch media url
                    media_info_url = f"https://graph.facebook.com/v18.0/{media_id}"
                    try:
                        media_info = requests.get(media_info_url, headers={'Authorization': f'Bearer {WHATSAPP_TOKEN}'}, timeout=12).json()
                        file_url = media_info.get('url')
                    except Exception as e:
                        print("media info error:", e)
                        file_url = None

                    if not file_url:
                        send_whatsapp_message(from_number, "Could not fetch image URL. Try again later.", phone_number_id)
                        continue

                    # download image bytes (Graph API may require same auth)
                    try:
                        image_resp = requests.get(file_url, headers={'Authorization': f'Bearer {WHATSAPP_TOKEN}'}, timeout=15)
                        if image_resp.status_code != 200:
                            raise Exception(f"image download status {image_resp.status_code}")
                        image_bytes = image_resp.content
                    except Exception as e:
                        print("image download error:", e)
                        send_whatsapp_message(from_number, "Failed to download image. Try again.", phone_number_id)
                        continue

                    # Save image to uploads and DB for training/inspection
                    try:
                        os.makedirs('uploads', exist_ok=True)
                        fname = f"{from_number}_{message_id}.jpg"
                        path = os.path.join('uploads', fname)
                        with open(path, 'wb') as f:
                            f.write(image_bytes)
                        farmer_images.insert_one({'phone': from_number, 'filename': path, 'ts': utc_now(), 'processed': False})
                    except Exception as e:
                        print("save image error:", e)

                    # If user is awaiting crop image (farmer flow)
                    if user_state.get(from_number, {}).get('mode') == 'farmer' and user_state[from_number].get('step') == 'awaiting_crop_image':
                        # call placeholder detector
                        result = farmer_crop_disease_detection(file_url)
                        send_whatsapp_message(from_number, result, phone_number_id)
                        # reset farmer step back to main farmer menu
                        user_state[from_number]['step'] = 'main'
                        send_whatsapp_message(from_number, FARMER_MENU, phone_number_id)
                        log_interaction(from_number, "[image]", result, extra={'mode':'farmer'})
                        continue
                    else:
                        # not expected image
                        send_whatsapp_message(from_number, "Image received. If you want crop diagnosis type 'farmer' and choose option 1.", phone_number_id)
                        log_interaction(from_number, "[image]", "saved (unexpected)", extra={'mode': user_state.get(from_number)})
                        continue

                # ---------- DOCUMENT (PDF) ----------
                if msg_type == 'document':
                    doc = msg.get('document', {}) or {}
                    media_id = doc.get('id')
                    mime = doc.get('mime_type','').lower()
                    if not media_id:
                        send_whatsapp_message(from_number, "Document id not found. Try again.", phone_number_id)
                        continue
                    if 'pdf' not in mime:
                        send_whatsapp_message(from_number, "Only PDF supported for summary.", phone_number_id)
                        continue

                    # get media url
                    media_info_url = f"https://graph.facebook.com/v18.0/{media_id}"
                    try:
                        media_info = requests.get(media_info_url, headers={'Authorization': f'Bearer {WHATSAPP_TOKEN}'}, timeout=12).json()
                        file_url = media_info.get('url')
                    except Exception as e:
                        print("pdf media info error:", e)
                        file_url = None

                    if not file_url:
                        send_whatsapp_message(from_number, "Could not fetch PDF URL. Try again later.", phone_number_id)
                        continue

                    # download PDF
                    try:
                        pdf_resp = requests.get(file_url, headers={'Authorization': f'Bearer {WHATSAPP_TOKEN}'}, timeout=20)
                        if pdf_resp.status_code != 200:
                            raise Exception(f"pdf download {pdf_resp.status_code}")
                        pdf_bytes = pdf_resp.content
                    except Exception as e:
                        print("pdf download error:", e)
                        send_whatsapp_message(from_number, "Failed to download PDF. Try again.", phone_number_id)
                        continue

                    # extract text
                    try:
                        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
                        raw_text = ""
                        for p in reader.pages:
                            raw_text += (p.extract_text() or "") + "\n"
                    except Exception as e:
                        print("pdf parse error:", e)
                        send_whatsapp_message(from_number, "Couldn't parse PDF text. Try a different PDF.", phone_number_id)
                        continue

                    # create summaries
                    raya_sum = extract_summary(raw_text, max_sentences=6) or "(No extractive summary)"
                    veda_sum = veda_ai_summary(raw_text)

                    reply = f"📑 R.A.Y.A Summary:\n{raya_sum[:1200]}\n\n🤖 V.E.D.A Summary:\n{veda_sum[:1200]}"
                    send_whatsapp_message(from_number, reply, phone_number_id)
                    log_interaction(from_number, "[pdf_uploaded]", reply, extra={'mode': user_state.get(from_number)})
                    continue

                # fallback for other types
                send_whatsapp_message(from_number, "Sorry, I can't process that message type yet.", phone_number_id)
                log_interaction(from_number, "[unsupported]", str(msg), extra={'mode': user_state.get(from_number)})
                continue

    # always respond 200 to Meta
    return "EVENT_RECEIVED", 200

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
