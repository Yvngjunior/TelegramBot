import requests
import time
import random
import os
from datetime import datetime

# =====================
# CONFIG
# =====================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise RuntimeError("Missing BOT_TOKEN or CHAT_ID environment variables")

ALLOWED_START_HOUR = 9
ALLOWED_END_HOUR = 22

MIN_DELAY = 300
MAX_DELAY = 600

CONTENT_DIR = "content"
USED_DIR = "used"
LOG_FILE = "bot.log"

# =====================
# UTILITIESi
# =====================

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def allowed_time():
    h = datetime.now().hour
    return ALLOWED_START_HOUR <= h <= ALLOWED_END_HOUR

# =====================
# CONTENT LOGIC
# =====================

def category_by_time():
    h = datetime.now().hour
    if 6 <= h < 11:
        return "morning"
    elif 11 <= h < 16:
        return "afternoon"
    elif 16 <= h < 21:
        return "evening"
    else:
        return "memes"

def load_lines(path):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return [l.strip() for l in f if l.strip()]

def get_post(category):
    content_file = f"{CONTENT_DIR}/{category}.txt"
    used_file = f"{USED_DIR}/{category}.used"

    all_lines = load_lines(content_file)
    used_lines = set(load_lines(used_file))

    if not all_lines:
        return f"[NO CONTENT in {category}]"

    available = [l for l in all_lines if l not in used_lines]

    if not available:
        open(used_file, "w").close()
        available = all_lines

    post = random.choice(available)

    with open(used_file, "a") as f:
        f.write(post + "\n")

    return post

# =====================
# TELEGRAM
# =====================

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        r = requests.post(url, data=data, timeout=15)
        log(f"Sent ({r.status_code})")
    except Exception as e:
        log(f"Telegram error: {e}")

# =====================
# MAIN LOOP
# =====================

os.makedirs(USED_DIR, exist_ok=True)
log("Bot started")

while True:
    if allowed_time():
        category = category_by_time()
        post = get_post(category)
        send_message(post)
    else:
        log("Skipped posting (outside allowed hours)")

    delay = random.randint(MIN_DELAY, MAX_DELAY)
    log(f"Sleeping for {delay} seconds")
    time.sleep(delay)
