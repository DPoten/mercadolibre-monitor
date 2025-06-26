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
POLL_INTERVAL = 60  # seconds
URL_FILE = "urls.json"

threads = []
running = True
previous_status = {}

def load_urls():
    try:
        with open(URL_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_urls(urls):
    with open(URL_FILE, "w") as f:
        json.dump(urls, f, indent=2)

def add_url(url):
    urls = load_urls()
    if url not in urls:
        urls.append(url)
        save_urls(url)
        start_monitor_for_url(url)  # start monitoring immediately

def remove_url(index):
    urls = load_urls()
    if 0 <= index < len(urls):
        urls.pop(index)
        save_urls(urls)

def get_urls():
    return load_urls()

def send_discord_notification(message):
    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
        print(f"Discord message sent, status code: {resp.status_code}")
    except Exception as e:
        print(f"Error sending Discord message: {e}")

def send_discord_embed(title, description, url, image_url):
    embed = {
        "title": title,
        "url": url,
        "description": description,
        "image": {"url": image_url} if image_url else {}
    }
    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]})
        print(f"Discord embed sent, status code: {resp.status_code}")
    except Exception as e:
        print(f"Error sending Discord embed: {e}")

def get_current_details(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if not resp.ok:
            print(f"Failed to fetch {url} with status {resp.status_code}")
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
    except Exception as e:
        print(f"Error fetching details from {url}: {e}")
        return None, None, None, None

def monitor_url(url):
    global running
    print(f"Started monitoring: {url}")
    while running:
        pct, price, img_url, name = get_current_details(url)
        if pct is not None and price is not None:
            prev_pct = previous_status.get(url)
            print(f"Checked {url}: discount={pct}% (prev {prev_pct}%)")
            # Only send notification if discount > 0 and changed
            if pct > 0 and (prev_pct is None or prev_pct != pct):
                previous_status[url] = pct
                discounted = price * (1 - pct / 100)
                desc = (
                    f"💰 **Original:** ${price:,.2f}\n"
                    f"🏷️ **{pct:.0f}% off:** Now ${discounted:,.2f}\n"
                    f"🛒 {name}\n{url}"
                )
                send_discord_embed(name, desc, url, img_url)
            else:
                previous_status[url] = pct  # Update even if no notification
        else:
            print(f"Could not retrieve data for {url}")
        time.sleep(POLL_INTERVAL)

def start_monitor_for_url(url):
    t = threading.Thread(target=monitor_url, args=(url,), daemon=True)
    t.start()
    threads.append(t)

def start_monitoring():
    urls = load_urls()
    if not urls:
        print("No URLs to monitor.")
        send_discord_notification("⚠️ Monitoring started, but no URLs to track yet.")
    else:
        print(f"Monitoring {len(urls)} URLs.")
        send_discord_notification(f"🚀 Monitoring started for {len(urls)} URLs.")
        for url in urls:
            start_monitor_for_url(url)

def stop_monitoring():
    global running
    running = False
