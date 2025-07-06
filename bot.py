import requests
from bs4 import BeautifulSoup
import time
import telegram
import os

# Environment variables (set in Railway)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = telegram.Bot(token=BOT_TOKEN)

headers = {
    "User-Agent": "Mozilla/5.0"
}

def scrape_iherb():
    try:
        bot.send_message(chat_id=CHANNEL_ID, text="👀 Bot started scraping iHerb...")
        
        url = "https://il.iherb.com/search?kw=probiotics"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select("div.product-card")

        bot.send_message(chat_id=CHANNEL_ID, text=f"🔍 Found {len(items)} items.")

        found_count = 0

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

            # For debug, show all products with "gmp" even if made in China
            if "gmp" in text:
                found_count += 1
                message = f"*שם מוצר:* {title}\n*מחיר:* {price}\n[לינק למוצר]({link})"
                bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=telegram.ParseMode.MARKDOWN)
                time.sleep(2)

                if found_count == 5:
                    break

        if found_count == 0:
            bot.send_message(chat_id=CHANNEL_ID, text="⚠️ No GMP products found.")
        else:
            bot.send_message(chat_id=CHANNEL_ID, text=f"✅ Posted {found_count} products.")

    except Exception as e:
        bot.send_message(chat_id=CHANNEL_ID, text=f"❌ Error: {str(e)}")

# Call the function on deploy
if __name__ == "__main__":
    scrape_iherb()
