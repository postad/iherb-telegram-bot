import requests
import telegram
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

bot = telegram.Bot(token=BOT_TOKEN)

def fetch_probiotics():
    url = "https://iherb-product-data-api.p.rapidapi.com/api/IHerb/GetProductByKeyword"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "iherb-product-data-api.p.rapidapi.com"
    }
    payload = {
        "keyword": "probiotic",
        "pageNumber": 1
    }

    response = requests.post(url, json=payload, headers=headers)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.text)

    try:
        data = response.json()
    except Exception as e:
        bot.send_message(chat_id=CHANNEL_ID, text=f"❌ שגיאה בפענוח JSON: {str(e)}")
        return

    count = 0
    bot.send_message(chat_id=CHANNEL_ID, text="🔍 בודק פרוביוטיקה מתחת ל־$15...")

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
        except Exception as e:
            print("Error parsing item:", str(e))
            continue

    if count == 0:
        bot.send_message(chat_id=CHANNEL_ID, text="ℹ️ לא נמצאו מוצרים מתאימים כרגע.")

if __name__ == "__main__":
    fetch_probiotics()
