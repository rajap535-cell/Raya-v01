# RAYA.py  -- cleaned CLI + utilities, delegates Q/A to engine.respond_to_query
# Corrected full file based on the version you provided. Keep a backup of your original.
import os
import re
import json
import csv
import time
import random
import sqlite3
import requests
import feedparser
import pywhatkit
import wikipedia
import pyfiglet
import pygame
from PIL import Image, ExifTags
from datetime import datetime, date, timezone
from heapq import nlargest
from bs4 import BeautifulSoup
from colorama import init, Fore
import PyPDF2
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'raya_core'))
from raya_core.orchestrator import ask_raya

# -------------------------
# Robust imports: prefer raya_core package if present, else local modules.
# -------------------------
respond_to_query = None
answer_question_func = None
detect_intents = None
search_topic_news = None

try:
    from raya_core.qa_engine import answer_question as _aq
    from raya_core.engine import respond_to_query as _rtq
    from raya_core.intent import detect_intents as _di
    from raya_core.source_news_topic import search_topic_news as _stn

    answer_question_func = _aq
    respond_to_query = _rtq
    detect_intents = _di
    search_topic_news = _stn
except Exception:
    try:
        # local fallback (if modules live in project root)
        import sys
        sys.path.append(os.path.dirname(__file__))  # ensure project root is importable
        # Attempt local module imports
        from raya_core.qa_engine import answer_question as _aq
        from raya_core.engine import respond_to_query as _rtq
        from raya_core.intent import detect_intents as _di
        from raya_core.source_news_topic import search_topic_news as _stn

        answer_question_func = _aq
        respond_to_query = _rtq
        detect_intents = _di
        search_topic_news = _stn
    except Exception:
        # Final fallback: keep None and handle gracefully at runtime
        answer_question_func = None
        respond_to_query = None
        detect_intents = None
        search_topic_news = None

# =========================
# CONFIG / DEV
# =========================
USER_ID = "local_user"
DB_FILE = "raya_conversation.db"
CACHE_PATH = "final_raya_cache.json"
init(autoreset=True)
DEV_MODE = True

# Ensure folders exist
os.makedirs("assets/images", exist_ok=True)
os.makedirs("assets/pdfs", exist_ok=True)
os.makedirs("exports", exist_ok=True)

# =========================
# DATABASE INITIALIZATION
# =========================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT,
            ai_output TEXT,
            message_type TEXT DEFAULT 'text',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS raya_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_id TEXT,
            data_type TEXT,
            content TEXT,
            tags TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS image_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            image_name TEXT,
            detected_objects TEXT,
            ai_description TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS pdf_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            pdf_name TEXT,
            extracted_text TEXT,
            summary TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS search_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            search_query TEXT,
            search_results TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS entity_aliases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_name TEXT,
            alias TEXT
        )
    ''')
    conn.commit()
    conn.close()

# =========================
# DATABASE UTILITIES
# =========================
def store_data(user_id, data_type, content, tags=""):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "INSERT INTO raya_data (timestamp, user_id, data_type, content, tags) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().isoformat(), user_id, data_type, content, tags)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] store_data error: {e}")

def save_conversation(user_input, ai_output, message_type="text"):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO conversations (user_input, ai_output, message_type) VALUES (?, ?, ?)",
                  (user_input, ai_output, message_type))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] save_conversation error: {e}")

def log_image_db(image_name, detected_objects, ai_description):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""INSERT INTO image_logs (timestamp, image_name, detected_objects, ai_description)
                     VALUES (?, ?, ?, ?)""",
                  (datetime.now().isoformat(), image_name, json.dumps(detected_objects), ai_description))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] log_image_db error: {e}")

def log_pdf_db(pdf_name, extracted_text, summary):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""INSERT INTO pdf_logs (timestamp, pdf_name, extracted_text, summary)
                     VALUES (?, ?, ?, ?)""",
                  (datetime.now().isoformat(), pdf_name, extracted_text, summary))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] log_pdf_db error: {e}")

def save_entity(entity_name: str):
    """Creates alias rows for an entity (keeps simple)."""
    aliases = generate_aliases(entity_name)
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        for alias in aliases:
            c.execute("INSERT INTO entity_aliases (entity_name, alias) VALUES (?, ?)", (entity_name, alias))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] save_entity error: {e}")

def resolve_entity(word: str) -> str:
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        lw = word.lower()
        c.execute("SELECT entity_name FROM entity_aliases WHERE alias = ? LIMIT 1", (lw,))
        row = c.fetchone()
        conn.close()
        if row:
            return row[0]
    except Exception as e:
        print(f"[DB] resolve_entity error: {e}")
    return word

# =========================
# ALIASES / CLEANER
# =========================
def generate_aliases(entity_name):
    aliases = set()
    aliases.add(entity_name.lower())
    aliases.add(entity_name.replace(" ", "").lower())
    parts = entity_name.split()
    if len(parts) > 1:
        aliases.add("".join([p[0] for p in parts]).lower())
    return list(aliases)

def clean_query(q: str) -> str:
    if not q:
        return ""
    qq = q.strip()
    qq = re.sub(r"\s+", " ", qq)
    qq = re.sub(r"^(who|whos|who's)\s+(is|was)\s+", "", qq, flags=re.I)
    qq = re.sub(r"^(what)\s+(is|are)\s+", "", qq, flags=re.I)
    qq = qq.strip(" ?!.,")
    return qq

# =========================
# IMAGE HANDLING
# =========================
def is_valid_image(path):
    try:
        with Image.open(path) as img:
            img.verify()
            fmt = (img.format or "").lower()
            return fmt in ["jpeg", "jpg", "png"]
    except Exception:
        return False

def process_image():
    image_path = input("Enter image path:").strip()
    try:
        img = Image.open(image_path)
        desc = f"Image {os.path.basename(image_path)} — {img.size} {img.mode}"
        print(f"Loaded: {desc}")
        save_conversation("user", f"[Uploaded image:{image_path}]", message_type="image")
        save_conversation("raya", "Image saved successfully", message_type="text")
        log_image_db(os.path.basename(image_path), [], desc)
        store_data(USER_ID, "image", desc, tags="")
        print("Image saved to database.")
    except Exception as e:
        print(f"Error loading image: {e}")

def analyze_image(image_path):
    if not os.path.exists(image_path):
        return "Image not found."
    if not is_valid_image(image_path):
        return "File is not a recognized JPEG/PNG image."
    try:
        with Image.open(image_path) as img:
            w, h = img.size
            mode = img.mode
            camera = "Unknown"
            try:
                raw_exif = img._getexif() or {}
                exif_data = {}
                for k, v in raw_exif.items():
                    tag = ExifTags.TAGS.get(k, k)
                    exif_data[tag] = v
                camera = exif_data.get("Model") or exif_data.get("Make") or "Unknown"
            except Exception:
                pass
            small = img.resize((32, 32))
            colors = small.getcolors(32*32) or []
            dominant_rgb = max(colors, key=lambda t: t[0])[1] if colors else (0,0,0)
            r,g,b = dominant_rgb[:3] if isinstance(dominant_rgb, tuple) else (0,0,0)
            tag_guess = "balanced"
            if g > r and g > b: tag_guess = "likely vegetation/outdoor"
            elif b > r and b > g: tag_guess = "likely sky/water"
            elif r > g and r > b: tag_guess = "likely warm/indoor or objects"
            desc = f"Image {os.path.basename(image_path)} — {w}x{h}px, mode {mode}. Camera: {camera}. Dominant RGB: {r},{g},{b} ({tag_guess})."
            log_image_db(os.path.basename(image_path), [], desc)
            store_data(USER_ID, "image", desc, tags=tag_guess)
            return desc
    except Exception as e:
        return f"Failed to analyze image: {e}"

# =========================
# PDF HANDLING
# =========================
def extract_pdf_text(pdf_path):
    if not os.path.exists(pdf_path):
        return ""
    text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        return f"[PDF read error] {e}"
    return text

def summarize_text(text, max_sentences=5):
    if not text:
        return ""
    sentences = re.split(r'(?<=[.!?])\s+|\n', text)
    word_freq = {}
    for word in re.findall(r"\b[a-zA-Z]{4,}\b", text.lower()):
        word_freq[word] = word_freq.get(word,0)+1
    scores = {}
    for s in sentences:
        score = sum(word_freq.get(w,0) for w in re.findall(r"\b[a-zA-Z]{4,}\b", s.lower()))
        if s.strip():
            scores[s] = score
    top = nlargest(max_sentences, scores, key=scores.get)
    return " ".join(top)

def process_pdf(pdf_path):
    extracted = extract_pdf_text(pdf_path)
    if not extracted:
        return "Couldn't extract text (file missing or unreadable)."
    summary = summarize_text(extracted, max_sentences=6)
    log_pdf_db(os.path.basename(pdf_path), extracted, summary)
    store_data(USER_ID, "pdf", f"PDF:{os.path.basename(pdf_path)} | len={len(extracted)}", tags="summary")
    return f"Summary of {os.path.basename(pdf_path)}:\n{summary}"

# =========================
# WEATHER & LOCATION
# =========================
def get_location_by_ip():
    try:
        response = requests.get("https://ipinfo.io", timeout=5)
        city = response.json().get("city", "")
        if city:
            print(f"RAYA SAY: Detected your current location as {city}")
            return city
        else:
            print("RAYA SAY: Couldn't detect your location. Please enter a city.")
            return ""
    except:
        print("RAYA SAY: Error fetching location info.")
        return ""

def get_weather(city=""):
    api_key = os.getenv("OPENWEATHER_API_KEY", "YOUR_OPENWEATHER_API_KEY")
    # If you have a hardcoded key, replace here (not recommended publicly)
    api_key = "45b55103e80aaae1a57e6bed22ee4245"
    if not api_key or api_key == "api_key":
        print("RAYA SAY: Weather API key not set.")
        return
    url = f"https://api.openweathermap.org/data/2.5/weather?appid={api_key}&q={city}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("cod") != "404":
            main = data["main"]
            weather_desc = data["weather"][0]["description"]
            temp = main["temp"]
            humidity = main["humidity"]
            out = f"Weather in {city} is {temp}℃ with {weather_desc}. Humidity is {humidity}%"
            print(f"\nRAYA SAY: {out}")
            save_conversation(f"weather {city}", out, message_type="text")
        else:
            print("RAYA SAY: Location not found")
    except Exception as e:
        print("RAYA SAY: Error fetching weather:", e)

# =========================
# NEWS SOURCES (interactive)
# =========================
def get_bbc_headlines():
    try:
        url = "https://www.bbc.com/news"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        headlines = [tag.get_text(strip=True) for tag in soup.find_all('h2') if tag.get_text(strip=True)]
        return headlines[:10]
    except Exception as e:
        print("[NEWS] get_bbc_headlines error:", e)
        return []

def get_cnn_headlines():
    try:
        url = "http://edition.cnn.com"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(response.text, "html.parser")
        headlines = []
        for span in soup.find_all("span", class_="container__headline-text"):
            text = span.get_text(strip=True)
            if text and 4 <= len(text.split()) <= 12 and text[0].isupper() and "," not in text:
                headlines.append(text)
        return headlines[:10]
    except Exception:
        return []

def get_ndtv_headlines():
    try:
        url = "https://feeds.feedburner.com/ndtvnews-top-stories"
        feed = feedparser.parse(url)
        return [entry.title for entry in feed.entries[:10]]
    except Exception:
        return []

def get_aljazeera_headlines():
    try:
        url = "https://aljazeera.com/xml/rss/all.xml"
        feed = feedparser.parse(url)
        return [entry.title for entry in feed.entries[:10]]
    except Exception:
        return []

# =========================
# HELPERS: fallback intent detector if module missing
# =========================
def _fallback_detect_intents(text: str):
    t = (text or "").strip().lower()
    if not t:
        return {"fact": 0.5}
    if t == "news":
        return {"news": 1.0}
    if t.startswith("news "):
        return {"news": 0.9}
    if re.search(r"^(who|what|when|where|why|how)\b", t) or "?" in t:
        return {"fact": 0.9, "qa": 0.7}
    return {"fact": 0.6, "qa": 0.5}

if detect_intents is None:
    detect_intents = _fallback_detect_intents

# =========================
# BRANDING/INTRO
# =========================
def branding_intro():
    if DEV_MODE:
        print("Raya Dev Mode: Skipping boot sequence.\n")
        return
    banner = pyfiglet.figlet_format("V.E.D.A", font="slant")
    print(Fore.CYAN + banner)
    print(Fore.YELLOW + "Civilization Protocols//Responsive Intelligence Tier 1.0")
    print(Fore.CYAN + "="*60)
    time.sleep(0.6)

# =========================
# MAIN CLI LOOP
# =========================
def main():
    init_db()
    branding_intro()

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue

        command = user_input.lower().strip()

        # Exit
        if command in ["exit", "quit", "bye"]:
            print("RAYA SAY: Shutting down. Have a great day!")
            break

        # Log raw input
        store_data(USER_ID, "text", user_input)

        # Fast local handlers (time/date/weather/joke/search/play/news sources)
        if "time" in command and command == "time":
            ans = f"The current time is {datetime.now().strftime('%H:%M:%S')}"
            print(f"RAYA SAY: {ans}")
            save_conversation(user_input, ans, message_type="text")
            continue

        if "date" in command and command == "date":
            ans = f"Today's date is {date.today()}"
            print(f"RAYA SAY: {ans}")
            save_conversation(user_input, ans, message_type="text")
            continue

        # ---- Weather handling ----
        if command.strip().lower() == "weather":
            city = input("RAYA SAY: Which city? (Leave blank to use your current location): ").strip()
            if not city:
                city = get_location_by_ip()
            if city:
                get_weather(city.strip().title())
            save_conversation(user_input, f"[weather:{city or 'auto'}]", message_type="text")
            continue

        elif command.startswith("what is weather") or command.startswith("how is weather") or command.startswith("explain weather"):
            # Conceptual question → engine or fallback text
            if respond_to_query:
                ans = respond_to_query(user_input, DB_FILE)
                out = ans if str(ans).lstrip().startswith("RAYA") else f"RAYA SAY: {ans}"
            else:
                out = "RAYA SAY: Weather is the state of the atmosphere at a given time and place."
            print(out)
            save_conversation(user_input, out, message_type="text")
            continue

        elif command.startswith("weather in") or command.startswith("forecast in") or command.startswith("temperature in"):
            if respond_to_query:
                ans = respond_to_query(user_input, DB_FILE)
                out = ans if str(ans).lstrip().startswith("RAYA") else f"RAYA SAY: {ans}"
            else:
                out = f"RAYA SAY: Fetching weather info for {command}..."
            print(out)
            save_conversation(user_input, out, message_type="text")
            continue

        # Jokes
        if "joke" in command or "jokes" in command:
            jokes = [
                "Why did the Python programmer go hungry? Because his food was in bytes!",
                "I told my code to clean the house. Now my laptop is gone."
            ]
            ans = random.choice(jokes)
            print(f"RAYA SAY: {ans}")
            save_conversation(user_input, ans, message_type="text")
            continue

        # Search / Play
        if command.startswith("search"):
            q = command.replace("search", "", 1).strip()
            print(f"RAYA SAY: Searching Google for {q}")
            try:
                pywhatkit.search(q)
            except Exception as e:
                print(f"RAYA SAY: Could not open browser: {e}")
            conn = sqlite3.connect(DB_FILE); c = conn.cursor()
            c.execute(
                "INSERT INTO search_logs (timestamp, search_query, search_results) VALUES (?, ?, ?)",
                (datetime.now().isoformat(), q, "opened in browser")
            )
            conn.commit(); conn.close()
            store_data(USER_ID, "search", q)
            save_conversation(user_input, f"Searched: {q}", message_type="text")
            continue

        if command.startswith("play"):
            song = command.replace("play", "", 1).strip()
            print(f"RAYA SAY: Playing {song} on YouTube")
            try:
                pywhatkit.playonyt(song)
            except Exception as e:
                print(f"RAYA SAY: Could not play: {e}")
            save_conversation(user_input, f"Played: {song}", message_type="text")
            continue

        # Interactive news menu (exact "news")
        if command.strip().lower() == "news":
            print("RAYA SAY: Fetching Top News Headlines.....")
            print("1. BBC\n2. CNN\n3. NDTV\n4. Al Jazeera")
            choice = input("Your choice (1/2/3/4): ").strip()
            headlines = []; source = ""
            if choice == "1": headlines = get_bbc_headlines(); source = "BBC"
            elif choice == "2": headlines = get_cnn_headlines(); source = "CNN"
            elif choice == "3": headlines = get_ndtv_headlines(); source = "NDTV"
            elif choice == "4": headlines = get_aljazeera_headlines(); source = "Al Jazeera"
            else:
                print("RAYA SAY: Invalid news source choice.")
            if headlines:
                ans = "Top 10 news from " + source + ":\n" + "\n".join([f"{i+1}. {h}" for i, h in enumerate(headlines)])
                out = f"RAYA SAY: {ans}"
                print(out)
                save_conversation(user_input, out, message_type="text")
            continue

        # Topic news: "news <topic>" or "latest news on ..."
        # --- Fixed RAYA.py News Topic Fetch ---
# This keeps your time/date/weather/news menu logic intact.
# Only improves the "latest news on <topic>" & "news <topic>" pipeline.

# Replace only the topic-news section:

        # Topic news: "news <topic>" or "latest news on ..."
        if "news" in command:
            if command.strip() != "news":  # exact 'news' is handled above
                topic = command
                for pat in [
                    "latest news on", "latest news about", "latest news of",
                    "recent news on", "recent news", "news today",
                    "news on", "news about", "news of", "latest news", "news"
                ]:
                    topic = re.sub(rf"\\b{pat}\\b", "", topic, flags=re.I)
                topic = topic.strip()
                if not topic:
                    topic = "latest"
                print(f"RAYA SAY: Fetching news on {topic}....")

                headlines = []
                try:
                    # Attempt live Google News RSS query if search_topic_news unavailable
                    if search_topic_news:
                        headlines = search_topic_news(topic, max_items=10)
                    else:
                        gnews_url = f"https://news.google.com/rss/search?q={requests.utils.quote(topic)}&hl=en-IN&gl=IN&ceid=IN:en"
                        feed = feedparser.parse(gnews_url)
                        headlines = [entry.title for entry in feed.entries[:10]]
                except Exception as e:
                    print(f"[NEWS] search_topic_news error: {e}")

                if headlines:
                    ans = "Here are some recent headlines:\n" + "\n".join([f"{i+1}. {h}" for i, h in enumerate(headlines)])
                    out = f"RAYA SAY: {ans}"
                    print(out)
                    save_conversation(user_input, out, message_type="text")
                else:
                    out = f"RAYA SAY: Sorry, I couldn’t find recent news about {topic}."
                    print(out)
                    save_conversation(user_input, out, message_type="text")
                continue

        # Image / PDF / Export handling
        if command == "upload image":
            process_image(); continue

        if command.startswith("image "):
            path = command.replace("image", "", 1).strip().strip('"').strip("'")
            ans = analyze_image(path)
            out = f"RAYA SAY: {ans}"
            print(out)
            save_conversation(user_input, out, message_type="text")
            continue

        if command.startswith("pdf "):
            path = command.replace("pdf", "", 1).strip().strip('"').strip("'")
            ans = process_pdf(path)
            out = f"RAYA SAY:\n{ans}"
            print(out)
            save_conversation(user_input, out, message_type="text")
            continue

        if command in ["export", "export data", "export all"]:
            conn = sqlite3.connect(DB_FILE); c = conn.cursor()
            tables = ["conversations","raya_data","image_logs","pdf_logs","search_logs"]
            for t in tables:
                rows = c.execute(f"SELECT * FROM {t}").fetchall()
                cols = [d[0] for d in c.description] if c.description else []
                csv_path = os.path.join("exports", f"{t}.csv")
                with open(csv_path,"w",newline="",encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(cols)
                    writer.writerows(rows)
                json_path = os.path.join("exports", f"{t}.json")
                dict_rows = [dict(zip(cols,r)) for r in rows]
                with open(json_path,"w",encoding="utf-8") as f:
                    json.dump(dict_rows,f,ensure_ascii=False, indent=2)
            conn.close()
            out = "RAYA SAY: Exported all data to the 'exports' folder."
            print(out)
            save_conversation(user_input, out, message_type="text")
            continue

        # ---- All other queries: delegate to QA engine or pipeline ----
        try:
            ans_obj = ask_raya(user_input)  # Returns object with .text
            out = f"RAYA SAY: {ans_obj.text}"
        except Exception as e:
            print(f"[ORCHESTRATOR] error: {e}")
            out = f"RAYA SAY: Sorry, I don't know the answer to that."

        print(out)
        save_conversation(user_input, out, message_type="text")

        # 1) Try QA engine (if available)
        if answer_question_func:
            try:
                qa_res = answer_question_func(user_input)
                # qa_engine returns an object wit-
                out = f"RAYA SAY: {ans}"
            finally: 
                print(out)
        save_conversation(user_input, out, message_type="text")
if __name__ == "__main__":
    main()
