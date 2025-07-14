import requests
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook
import time

WEBHOOK_URL = "https://discord.com/api/webhooks/1394384425038512240/BmO35657wTNWukr8_UCG2dbbdjSvJnnCy2xBavtC5PwXaSY7JE_g5tY1aVPBPXeOroib"  # Replace with your actual webhook

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

SITES = {
    "B&H": "https://www.bhphotovideo.com/c/product/1769033-REG/fujifilm_16821328_x100vi_digital_camera_silver.html",
    "Adorama": "https://www.adorama.com/ifjx100vis.html",
    "Best Buy": "https://www.bestbuy.com/site/fujifilm-x100vi-digital-camera-silver/6577751.p"
}


def notify(store, url, price):
    """Send a Discord alert."""
    message = f"🟢 **{store}** has the Fujifilm X100VI in stock for **${price}**!\n🔗 {url}"
    webhook = DiscordWebhook(url=WEBHOOK_URL, content=message)
    webhook.execute()
    print(f"[+] Sent alert for {store} at ${price}")


def parse_price(text):
    """Extracts float price from text like '$1,599.00'."""
    try:
        return float(text.replace('$', '').replace(',', '').strip())
    except:
        return None


def check_bh():
    url = SITES["B&H"]
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    stock = soup.select_one(".stockStatus")
    price = soup.select_one(".price_1DPoToKrLP8uWvruGqgtaY")

    if stock and "In Stock" in stock.text and price:
        p = parse_price(price.text)
        if p and p < 1700:
            notify("B&H Photo", url, p)


def check_adorama():
    url = SITES["Adorama"]
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    stock = soup.select_one("#stockAvailability")
    price = soup.select_one("div#pricing span.your-price")

    if stock and "In Stock" in stock.text and price:
        p = parse_price(price.text)
        if p and p < 1700:
            notify("Adorama", url, p)


def check_bestbuy():
    url = SITES["Best Buy"]
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    if "Sold Out" not in r.text and "Add to Cart" in r.text:
        price_tag = soup.select_one(".priceView-hero-price span")
        if price_tag:
            p = parse_price(price_tag.text)
            if p and p < 1700:
                notify("Best Buy", url, p)


def run():
    while True:
        print("🔄 Checking stock...")
        try: check_bh()
        except Exception as e: print("❌ B&H error:", e)

        try: check_adorama()
        except Exception as e: print("❌ Adorama error:", e)

        try: check_bestbuy()
        except Exception as e: print("❌ Best Buy error:", e)

        time.sleep(45)  # wait 45 seconds between checks


if __name__ == "__main__":
    run()
