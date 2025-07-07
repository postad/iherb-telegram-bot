import requests
import telegram
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

bot = telegram.Bot(token=BOT_TOKEN)

def fetch_probiotics():
    url = "https://iherb-product-data-api.p.rapidapi.com/api/IHerb/GetProductByBrandName"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "iherb-product-data-api.p.rapidapi.com"
    }
    payload = {
        "brandName": "probiotic",
        "pageNumber": 1
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    count = 0
    for item in data.get("data", []):
        try:
            title = item["productName"]
            price = float(item["salePrice"].replace("$", ""))
            link = item["productUrl"]

            if price < 15:
                msg = f"*שם מוצר:* {title}\n*מחיר:* ${price}\n[לינק למוצר]({link})"
                bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)
                count += 1
            if count >= 5:
                break
        except Exception:
            continue

if __name__ == "__main__":
    fetch_probiotics()
