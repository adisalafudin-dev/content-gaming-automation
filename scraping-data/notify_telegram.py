import os, time, requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SITE_URL = (os.getenv("SITE_URL") or "").rstrip("/")


def send(text):
    # Teks polos (tanpa parse_mode) supaya karakter khusus tidak bikin error
    for i in range(0, len(text), 4000):  # batas Telegram 4096 karakter
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": text[i:i + 4000],
                "disable_web_page_preview": True,
            },
            timeout=30,
        )
        r.raise_for_status()
        time.sleep(1)


def article_url(article):
    return f"{SITE_URL}/artikel/{article['slug']}/"


def send_threads():
    rows = (
        sb.table("threads")
        .select("id, content, articles(title, slug)")
        .eq("status", "pending")
        .order("created_at")
        .limit(10)
        .execute()
        .data
    )
    for row in rows:
        art = row["articles"]
        send(f"🐦 THREAD\n📰 {art['title']}")
        tweets = [t.strip() for t in row["content"].split("\n\n") if t.strip()]
        for t in tweets:
            send(t)   # satu pesan per tweet, tinggal salin-tempel
        send(f"🔗 Baca selengkapnya:\n{article_url(art)}")
        sb.table("threads").update({"status": "sent"}).eq("id", row["id"]).execute()
        print(f"✅ Thread terkirim: {art['title']}")
    return len(rows)


def send_shorts():
    rows = (
        sb.table("shorts_scripts")
        .select("id, script, articles(title, slug)")
        .eq("status", "pending")
        .order("created_at")
        .limit(10)
        .execute()
        .data
    )
    for row in rows:
        art = row["articles"]
        send(f"🎬 NASKAH SHORTS\n📰 {art['title']}\n\n{row['script']}")
        sb.table("shorts_scripts").update({"status": "sent"}).eq("id", row["id"]).execute()
        print(f"✅ Naskah terkirim: {art['title']}")
    return len(rows)


if __name__ == "__main__":
    if not TOKEN or not CHAT_ID:
        raise SystemExit("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID belum diset")
    t = send_threads()
    s = send_shorts()
    print(f"Selesai: {t} thread, {s} naskah")