import os
import telegram
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

bot = telegram.Bot(token=BOT_TOKEN)

# קטגוריה -> רשימת מותגים מועדפים
CATEGORY_BRANDS = {
    "ויטמין C": ["Now Foods", "Doctor's Best", "Solgar", "California Gold Nutrition"],
    "פרוביוטיקה": ["California Gold Nutrition", "Renew Life", "Garden of Life"]
}

def fetch_products_by_category(category):
    brands = CATEGORY_BRANDS.get(category, [])
    if not brands:
        bot.send_message(chat_id=CHANNEL_ID, text=f"❌ לא נמצאו מותגים מתאימים לקטגוריה '{category}'")
        return

    bot.send_message(chat_id=CHANNEL_ID, text=f"🔍 מחפש מוצרים פופולריים מתוך הקטגוריה: {category}...")
    count = 0

    for brand in brands:
        url = f"https://iherb-product-data-api.p.rapidapi.com/brands/{brand}/products"
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "iherb-product-data-api.p.rapidapi.com"
        }
        params = {
            "page": 1,
            "hasStock": True,
            "minRating": 4.5
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            continue

        try:
            data = response.json()
        except:
            continue

        for item in data.get("products", []):
            try:
                title = item["title"]
                price = item["formattedPrice"]
                link = item["link"]
                rating = item["ratingValue"]

                msg = f"*{title}*
מחיר: {price} ⭐️ דירוג: {rating}
[לינק למוצר]({link})"
                bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)
                count += 1
                if count >= 10:
                    return
            except:
                continue

    if count == 0:
        bot.send_message(chat_id=CHANNEL_ID, text="ℹ️ לא נמצאו מוצרים פופולריים לקטגוריה זו.")

if __name__ == "__main__":
    fetch_products_by_category("ויטמין C")
