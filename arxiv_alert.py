import feedparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser
import os
from dotenv import load_dotenv

# ========== SETTINGS ==========
DEBUG = False

KEYWORDS = [
    "cdex",
    "xenonnt",
    "lz",
    "pandax",
    "hydrox",
    "tesseract",
    "dark matter",
    "direct detection",
    "neutrinoless double beta",
    "double-weak",
    "xenon",
    "neutrino physics",
    "2νββ",
]

EXCLUDED_KEYWORDS = [
    "alice",
    "LHC"
]

CATEGORIES = ["hep-ex", "hep-ph", "nucl-ex",]
CATEGORIES_EXCLUDED = ["astro-ph.GA","astro-ph.CO","astro-ph.SR","astro-ph.HE","astro-ph.EP","astro-ph.IM"]

BASE_URL = "http://export.arxiv.org/api/query?search_query="
SEEN_IDS_FILE = "seen_ids.txt"
# ==============================

# Load environment variables from .env
load_dotenv()
EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT"))
TO_EMAIL = os.getenv("TO_EMAIL")

def build_query():
    category_query = "+OR+".join([f"cat:{cat}" for cat in CATEGORIES])
    return f"{BASE_URL}{category_query}&sortBy=submittedDate&sortOrder=descending&max_results=2000"

def fetch_entries():
    query_url = build_query()
    feed = feedparser.parse(query_url)
    if DEBUG:
        print(f"🔍 Fetching from: {query_url}")
        print(f"📚 Retrieved {len(feed.entries)} entries")
    return feed.entries

def load_seen_ids():
    if os.path.exists(SEEN_IDS_FILE):
        with open(SEEN_IDS_FILE, "r") as f:
            seen = set(line.strip() for line in f.readlines())
            if DEBUG:
                print(f"📁 Loaded {len(seen)} seen IDs")
            return seen
    return set()

def save_seen_ids(ids):
    with open(SEEN_IDS_FILE, "a") as f:
        for arxiv_id in ids:
            f.write(arxiv_id + "\n")
    if DEBUG:
        print(f"💾 Saved {len(ids)} new IDs to {SEEN_IDS_FILE}")

def is_recent(published_str):
    published_date = date_parser.parse(published_str)
    one_day_ago = datetime.now(timezone.utc) - timedelta(days=7)
    return published_date > one_day_ago

def filter_entries(entries, seen_ids):
    new_entries = []
    new_ids = []
    for entry in entries:
        if entry.id in seen_ids:
            if DEBUG:
                print(f"⏩ Skipping already seen: {entry.title}")
            continue
        if not is_recent(entry.published):
            if DEBUG:
                print(f"📅 Too old: {entry.title} ({entry.published})")
            continue
        text = f"{entry.title} {entry.summary}".lower()

        # Exclude by category tag if needed
        entry_categories = [tag['term'] for tag in entry.tags] if 'tags' in entry else []
        if any(cat in entry_categories for cat in CATEGORIES_EXCLUDED):
            if DEBUG:
                print(f"🚫 Excluded by category: {entry.title} — tags: {entry_categories}")
            continue

        # Check exclusion first
        if any(ex_kw.lower() in text for ex_kw in EXCLUDED_KEYWORDS):
            if DEBUG:
                print(f"🚫 Excluded by keyword: {entry.title}")
            continue

        matches = [kw for kw in KEYWORDS if kw.lower() in text]
        if matches:
            new_entries.append(entry)
            new_ids.append(entry.id)
            if DEBUG:
                print(f"✅ MATCH: {entry.title} — matched on: {', '.join(matches)}")
        else:
            if DEBUG:
                print(f"❌ No keyword match: {entry.title}")
    return new_entries, new_ids

def format_email(entries):
    html = "<h2>🧪 Custom New arXiv Papers Newsletter</h2><ul>"
    for entry in entries:
        html += f"<li><a href='{entry.link}'><b>{entry.title}</b></a><br>"
        html += f"<i>{entry.published}</i><br>"
        html += f"{entry.summary[:500]}...</li><br><br>"
    html += "</ul>"
    return html

def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, TO_EMAIL, msg.as_string())
    if DEBUG:
        print(f"📧 Email sent to {TO_EMAIL}")

def main():
    seen_ids = load_seen_ids()
    entries = fetch_entries()
    relevant_entries, new_ids = filter_entries(entries, seen_ids)

    if relevant_entries:
        html_body = format_email(relevant_entries)
        send_email("🆕 Custom arXiv Newsletter", html_body)
        save_seen_ids(new_ids)
        print(f"✅ Sent {len(relevant_entries)} paper(s).")
    else:
        print("ℹ️ No new relevant papers found.")

if __name__ == "__main__":
    main()
