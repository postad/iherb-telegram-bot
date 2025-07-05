import requests
from bs4 import BeautifulSoup
import time
import telegram
import os

# Environment variables (set these in Railway)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = telegram.Bot(token=BOT_TOKEN)

headers = {
    "User-Agent": "Mozilla/5.0"
}

def scrape_iherb():
    url = "https://il.iherb.com/search?kw=probiotics"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select("div.product-card")

    for item in items:
        title_tag = item.select_one("a.link")
        price_tag = item.select_one("div.price")
        if not title_tag or not price_tag:
            continue
        title = title_tag.get_text(strip=True)
        link = "https://il.iherb.com" + title_tag.get("href")
        price = price_tag.get_text(strip=True)

        # Visit product page to check GMP and origin
        product_page = requests.get(link, headers=headers)
        product_soup = BeautifulSoup(product_page.text, "html.parser")
        overview_div = product_soup.find("div", {"id": "product-overview"})
        text = overview_div.get_text().lower() if overview_div else ""

        if "gmp" in text and "made in china" not in text:
            message = f"*שם מוצר:* {title}\n*מחיר:* {price}\n[לינק למוצר]({link})"
            bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=telegram.ParseMode.MARKDOWN)
            time.sleep(2)

if __name__ == "__main__":
    scrape_iherb()
