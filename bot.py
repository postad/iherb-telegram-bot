import requests
from bs4 import BeautifulSoup
import telegram
import os
import time

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = telegram.Bot(token=BOT_TOKEN)

headers = {
    "User-Agent": "Mozilla/5.0"
}

def scrape_iherb():
    bot.send_message(chat_id=CHANNEL_ID, text="👀 Bot started scraping iHerb...")

    url = "https://il.iherb.com/search?kw=probiotics"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select("div.product-cell-container")
    bot.send_message(chat_id=CHANNEL_ID, text=f"🔍 Found {len(items)} items.")

    count = 0
    for item in items:
        title_tag = item.select_one("a.product-title")
        price_tag = item.select_one("div.price")

        if not title_tag or not price_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = "https://il.iherb.com" + title_tag.get("href")
        price = price_tag.get_text(strip=True)

        # Send raw product name for debugging
        bot.send_message(chat_id=CHANNEL_ID, text=f"🧪 Found product: {title}")

        # Check for GMP and not made in China
        product_page = requests.get(link, headers=headers)
        product_soup = BeautifulSoup(product_page.text, "html.parser")
        overview_div = product_soup.find("div", {"id": "product-overview"})
        text = overview_div.get_text().lower() if overview_div else ""

        if "gmp" in text and "made in china" not in text:
            message = f"*שם מוצר:* {title}\n*מחיר:* {price}\n[לינק למוצר]({link})"
            bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=telegram.ParseMode.MARKDOWN)
            count += 1
            time.sleep(2)

    if count == 0:
        bot.send_message(chat_id=CHANNEL_ID, text="⚠️ No GMP products found.")
    else:
        bot.send_message(chat_id=CHANNEL_ID, text=f"✅ Found {count} GMP product(s).")

# Trigger scraping directly
scrape_iherb()
