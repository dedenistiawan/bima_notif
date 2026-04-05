import requests
from bs4 import BeautifulSoup
import json
import os

TOKEN = os.getenv("8552942697:AAGbukBgA8vJ-QPAKt4HTD79verTjAh1VpI")
CHAT_ID = os.getenv("158052383")

URL = "https://bima.kemdiktisaintek.go.id/pengumuman"
DATA_FILE = "last_data.json"


def get_pengumuman():
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "html.parser")

    data = []
    items = soup.select("h3 a")

    for item in items:
        title = item.text.strip()
        link = item.get("href")

        if not link.startswith("http"):
            link = "https://bima.kemdiktisaintek.go.id" + link

        data.append({
            "title": title,
            "link": link
        })

    return data


def load_last_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)


def main():
    latest = get_pengumuman()
    last = load_last_data()

    last_titles = [x["title"] for x in last]
    new_items = [x for x in latest if x["title"] not in last_titles]

    for item in new_items:
        message = f"<b>{item['title']}</b>\n{item['link']}"
        send_telegram(message)

    save_data(latest)


if __name__ == "__main__":
    main()
