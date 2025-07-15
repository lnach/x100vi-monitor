import os
import time
import requests
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
ALERT_CACHE = {}

PRODUCTS = [
    {
        "name": "X100VI (Silver)",
        "store": "B&H",
        "url": "https://www.bhphotovideo.com/c/product/1899777-REG/fujifilm_16953912_x100vi_digital_camera_silver_coo_japan.html"
    },
    {
        "name": "X100VI (Black)",
        "store": "B&H",
        "url": "https://www.bhphotovideo.com/c/product/1899778-REG/fujifilm_16953924_x100vi_digital_camera_black_coo_japan.html"
    },
    {
        "name": "X100VI (Black)",
        "store": "Adorama",
        "url": "https://www.adorama.com/ifjx1006b.html"
    },
    {
        "name": "X100VI (Silver)",
        "store": "Adorama",
        "url": "https://www.adorama.com/ifjx1006s.html"
    },
    {
        "name": "X100VI (Silver)",
        "store": "Best Buy",
        "url": "https://www.bestbuy.com/site/fujifilm-x-series-x100vi-40-2mp-digital-camera-silver/6574272.p?skuId=6574272"
    },
    {
        "name": "X100VI (Black)",
        "store": "Best Buy",
        "url": "https://www.bestbuy.com/site/fujifilm-x-series-x100vi-40-2mp-digital-camera-black/6574274.p?skuId=6574274"
    }
]

def parse_price(text):
    try:
        return float(text.replace('$', '').replace(',', '').strip())
    except:
        return None

def notify(product_name, store, url, price):
    key = f"{store}:{product_name}"
    if ALERT_CACHE.get(key) == price:
        print(f"[SKIPPED] Duplicate alert for {key}")
        return
    ALERT_CACHE[key] = price

    webhook = DiscordWebhook(url=WEBHOOK_URL)
    embed = DiscordEmbed(
        title=f'{store} | {product_name}',
        description=f'**In stock for ${price}**',
        color='03b2f8'
    )
    embed.set_url(url)
    embed.set_footer(text='Fujifilm Stock Monitor')
    embed.set_timestamp()
    embed.add_embed_field(name='Store', value=store)
    embed.add_embed_field(name='Price', value=f"${price}")
    embed.add_embed_field(name='Link', value=f"[Buy now]({url})", inline=False)

    webhook.add_embed(embed)
    webhook.execute()
    print(f"[✅] Alert sent: {store} | {product_name} | ${price}")

def check_bh(product):
    print(f"[🔎] Checking B&H: {product['name']}")
    try:
        r = requests.get(product["url"], headers=HEADERS, timeout=10)
        print(f"[📄] Fetched B&H page, status: {r.status_code}")
        soup = BeautifulSoup(r.text, "html.parser")
        stock = soup.select_one(".stockStatus")
        price = soup.select_one(".price_1DPoToKrLP8uWvruGqgtaY")

        if stock and "In Stock" in stock.text and price:
            p = parse_price(price.text)
            if p and p < 1700:
                notify(product["name"], product["store"], product["url"], p)
    except Exception as e:
        print(f"[❌] B&H error for {product['name']}: {e}")

def check_adorama(product):
    print(f"[🔎] Checking Adorama: {product['name']}")
    try:
        r = requests.get(product["url"], headers=HEADERS, timeout=10)
        print(f"[📄] Fetched Adorama page, status: {r.status_code}")
        soup = BeautifulSoup(r.text, "html.parser")
        stock = soup.select_one("#stockAvailability")
        price = soup.select_one("div#pricing span.your-price")

        if stock and "In Stock" in stock.text and price:
            p = parse_price(price.text)
            if p and p < 1700:
                notify(product["name"], product["store"], product["url"], p)
    except Exception as e:
        print(f"[❌] Adorama error for {product['name']}: {e}")

def check_bestbuy(product):
    print(f"[🔎] Checking Best Buy: {product['name']}")
    try:
        r = requests.get(product["url"], headers=HEADERS, timeout=10)
        print(f"[📄] Fetched Best Buy page, status: {r.status_code}")
        soup = BeautifulSoup(r.text, "html.parser")

        if "Sold Out" not in r.text and "Add to Cart" in r.text:
            price_tag = soup.select_one(".priceView-hero-price span")
            if price_tag:
                p = parse_price(price_tag.text)
                if p and p < 1700:
                    notify(product["name"], product["store"], product["url"], p)
    except Exception as e:
        print(f"[❌] Best Buy error for {product['name']}: {e}")

STORE_CHECKS = {
    "B&H": check_bh,
    "Adorama": check_adorama,
    "Best Buy": check_bestbuy
}

def run():
    print("🔄 Starting stock check loop...")
    for product in PRODUCTS:
        check_fn = STORE_CHECKS.get(product["store"])
        if check_fn:
            check_fn(product)
        else:
            print(f"[⚠️] No check function for store: {product['store']}")
    print("✅ Cycle complete.")

if __name__ == "__main__":
    run()