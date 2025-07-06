import requests
from bs4 import BeautifulSoup
import time
import telegram
import os

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

    gmp_found = 0

    for item in items:
        title_tag = item.select_one("a.link")
        price_tag = item.select_one("div.price")
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

        if "gmp" in text:
            message = f"*[GMP Product {gmp_found+1}]*\n*שם מוצר:* {title}\n*מחיר:* {price}\n[לינק למוצר]({link})"
            bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=telegram.ParseMode.MARKDOWN)
            gmp_found += 1
            time.sleep(2)

        if gmp_found >= 5:
            break
