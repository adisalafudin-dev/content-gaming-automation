import os, json, time
from google import genai
from google.genai import types
from dotenv import load_dotenv
import feedparser
import re
import hashlib
from urllib.parse import urlparse
from supabase import create_client

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

MODEL = "models/gemini-3.8-flash"   # cek nama model terbaru di AI Studio

SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "judul_seo": {"type": "STRING"},
        "artikel_web": {"type": "STRING"},
        "twitter_thread": {"type": "STRING"},
        "shorts_script": {"type": "STRING"},
    },
    "required": ["judul_seo", "artikel_web", "twitter_thread", "shorts_script"],
}

FEEDS = [
    "https://www.pcgamer.com/rss/",
    "https://wccftech.com/feed/",
    "https://feeds.ign.com/ign/games-all",
]

def get_latest_news(limit=5):
    items = []
    for url in FEEDS:
        feed = feedparser.parse(url)
        for e in feed.entries[:2]:
            items.append({
                "title": e.title,
                "summary": re.sub(r"<[^>]+>", "", e.get("summary", "")),
                "link": e.link,
            })
    return items[:limit]

def parse_json_safely(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        return json.loads(m.group(0)) if m else None
    
    
def generate_content_assets(news, retries=3):
    print(f"🤖 Memproses: {news['title']}")
    prompt = (
        "Kamu jurnalis gaming profesional. Terjemahkan ke bahasa Indonesia dan buat 4 field: "
        "judul_seo (clickbait tapi relevan), artikel_web (HTML dengan <p>/<h2>, minimal 300 kata), "
        "twitter_thread (maks 3 tweet, santai + emoji, pisah dengan baris kosong), "
        "shorts_script (narasi voiceover 60 detik, teks saja).\n\n"
        f"Judul asli: {news['title']}\nRingkasan: {news['summary']}"
    )
    for attempt in range(retries):
        try:
            resp = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=SCHEMA,
                    temperature=0.7,
                ),
            )
            return json.loads(resp.text)
        except Exception as e:
            print(f"⚠️ Percobaan {attempt+1} gagal: {e}")
            time.sleep(10 * (attempt + 1))
    return None

def already_processed(link):
    res = sb.table("articles").select("id").eq("source_link", link).limit(1).execute()
    return len(res.data) > 0

def make_slug(title, link):
    base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:70]
    suffix = hashlib.md5(link.encode()).hexdigest()[:6]
    return f"{base}-{suffix}"

def save_assets(assets, news):
    article = sb.table("articles").insert({
        "slug": make_slug(assets["judul_seo"], news["link"]),
        "title": assets["judul_seo"],
        "content_html": assets["artikel_web"],
        "source_link": news["link"],
        "source_name": urlparse(news["link"]).netloc,
    }).execute().data[0]

    sb.table("threads").insert({
        "article_id": article["id"],
        "content": assets["twitter_thread"],
    }).execute()

    sb.table("shorts_scripts").insert({
        "article_id": article["id"],
        "script": assets["shorts_script"],
    }).execute()

    return article["slug"]


def main():
    for news in get_latest_news():
        if already_processed(news["link"]):
            print(f"⏭️ Sudah diproses: {news['title']}")
            continue

        assets = generate_content_assets(news)
        if not assets:
            print(f"❌ Gagal generate: {news['title']}")
            continue

        slug = save_assets(assets, news)
        print(f"✅ Tersimpan: {slug}")
        time.sleep(7)   # jaga RPM Gemini

if __name__ == "__main__":
    main()