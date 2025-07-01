import requests
import threading
import time
import json
from bs4 import BeautifulSoup

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1211442887380705340/_9UD6AaXJoEFYhSUrfZ71vpgEE2ZsB-V9hEsUEshOrt657KttCSyoxnfefLjCtiFTt8n"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}
POLL_INTERVAL = 3600  # 1 hour
URL_FILE = "urls.json"
previous_status = {}

def load_urls():
    try:
        with open(URL_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def get_current_details(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if not resp.ok:
            return None, None, None, None
        soup = BeautifulSoup(resp.content, "html.parser")

        frac = soup.select_one("span.andes-money-amount__fraction")
        dec = soup.select_one("span.andes-money-amount__decimals")
        price = float(frac.text.replace(".", "") + "." + (dec.text if dec else "00"))

        pct_el = soup.select_one("span.andes-money-amount__discount")
        pct = float(pct_el.text.strip().split("%")[0]) if pct_el else 0

        title_el = soup.select_one("h1.ui-pdp-title")
        name = title_el.text.strip() if title_el else "Unknown"

        img_meta = soup.select_one("meta[property='og:image']")
        img_url = img_meta["content"] if img_meta else None

        return pct, price, img_url, name
    except:
        return None, None, None, None

def send_discord_embed(title, description, url, image_url):
    embed = {
        "title": title,
        "url": url,
        "description": description,
        "image": {"url": image_url} if image_url else {}
    }
    try:
        r = requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]})
        print(f"[{title}] Discord status code: {r.status_code}")
    except Exception as e:
        print(f"Failed to send embed: {e}")

def monitor_loop():
    print("✅ Monitor started.")
    while True:
        urls = load_urls()
        for url in urls:
            pct, price, img_url, name = get_current_details(url)
            if pct is not None and price is not None:
                prev_pct = previous_status.get(url)
                if prev_pct is None or prev_pct != pct:
                    previous_status[url] = pct
                    discounted = price * (1 - pct / 100)
                    desc = (
                        f"💰 **Original:** ${price:,.2f}\n"
                        f"🏷️ **{pct:.0f}% off:** Now ${discounted:,.2f}\n"
                        f"🛒 {name}\n{url}"
                    )
                    send_discord_embed(name, desc, url, img_url)
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    monitor_loop()
