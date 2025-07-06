import requests
from bs4 import BeautifulSoup
import telegram
import os

# Environment variables (from Railway)
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

    # Debug preview of fetched HTML (first 4000 chars to avoid Telegram limit)
    bot.send_message(chat_id=CHANNEL_ID, text=soup.prettify()[:4000])

    items = soup.select("div.js-product-list div.product-inner")
    bot.send_message(chat_id=CHANNEL_ID, text=f"🔍 Found {len(items)} items.")

    gmp_count = 0

    for item in items[:5]:  # Limit to first 5 items for testing
        title_tag = item.select_one("a.product-title")
        price_tag = item.select_one("div.price-regular") or item.select_one("div.price")

        if not title_tag or not price_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = "https://il.iherb.com" + title_tag.get("href")
        price = price_tag.get_text(strip=True)

        # Visit product page
        product_page = requests.get(link, headers=headers)
        product_soup = BeautifulSoup(product_page.text, "html.parser")
        overview_div = product_soup.find("div", {"id": "product-overview"})
        text = overview_div.get_text().lower() if overview_div else ""

        if "gmp" in text and "made in china" not in text:
            gmp_count += 1
            message = f"*שם מוצר:* {title}\n*מחיר:* {price}\n[🔗 לינק למוצר]({link})"
            bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

    if gmp_count == 0:
        bot.send_message(chat_id=CHANNEL_ID, text="⚠️ No GMP products found.")
    else:
        bot.send_message(chat_id=CHANNEL_ID, text=f"✅ Found {gmp_count} GMP products.")

# Run immediately
scrape_iherb()
