import requests
from bs4 import BeautifulSoup
import json
import os
import urllib3

# Disable warning SSL (karena website pemerintah kadang error SSL)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://bima.kemdiktisaintek.go.id/pengumuman"

BOT_TOKEN = os.getenv("8552942697:AAGbukBgA8vJ-QPAKt4HTD79verTjAh1VpI")
CHAT_ID = os.getenv("158052383")

DATA_FILE = "last_data.json"


# Ambil data pengumuman dari website
def get_pengumuman():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        res = requests.get(URL, headers=headers, verify=False, timeout=10)
    except Exception as e:
        print("Error request:", e)
        return []

    soup = BeautifulSoup(res.text, "html.parser")

    items = soup.select("h3 a")

    data = []

    if not items:
        print("Tidak menemukan pengumuman")
        return []

    for item in items:
        title = item.text.strip()
        link = item.get("href")

        if not link:
            continue

        if not link.startswith("http"):
            link = "https://bima.kemdiktisaintek.go.id" + link

        data.append({
            "title": title,
            "link": link
        })

    return data


# Load data lama
def load_last_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


# Simpan data terbaru
def save_last_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


# Kirim pesan ke Telegram
def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Error kirim Telegram:", e)


def main():
    print("Ambil data terbaru...")
    latest = get_pengumuman()
    last = load_last_data()

    print("Latest:", len(latest))
    print("Last:", len(last))

    # Ambil data baru saja
    new_items = [item for item in latest if item not in last]

    if not new_items:
        print("Tidak ada pengumuman baru")
    else:
        print(f"Ada {len(new_items)} pengumuman baru")

        for item in new_items:
            message = f"<b>{item['title']}</b>\n{item['link']}"
            send_telegram(message)

    # Simpan data terbaru
    save_last_data(latest)


if __name__ == "__main__":
    main()
