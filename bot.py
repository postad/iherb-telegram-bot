import requests
import telegram
import os
import json # Import json for better error handling

# --- Configuration (from Environment Variables) ---
# It's crucial to set these environment variables in your Railway project
# and on your local machine if you're testing locally.
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

# --- Initialize Telegram Bot ---
# Ensure BOT_TOKEN is available when the script starts.
if not BOT_TOKEN:
    print("Error: BOT_TOKEN environment variable not set.")
    # In a real deployment, you might want to exit or log this more robustly.
    # For now, we'll proceed, but the bot won't send messages.
    bot = None # Set bot to None if token is missing
else:
    bot = telegram.Bot(token=BOT_TOKEN)

def send_telegram_message(message: str):
    """Helper function to send messages to Telegram, handling bot initialization."""
    if bot and CHANNEL_ID:
        try:
            bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=telegram.ParseMode.MARKDOWN)
        except telegram.error.TelegramError as e:
            print(f"Error sending Telegram message: {e}")
            print(f"Message content: {message}")
    else:
        print(f"Telegram bot not initialized or CHANNEL_ID missing. Message not sent: {message}")

def fetch_now_foods_products():
    """
    Fetches the first 20 products from the 'NOW Foods' brand using the
    RapidAPI iHerb 'Get Product By Brand Name' endpoint and sends them
    to a Telegram channel.
    """
    # --- API Endpoint and Headers ---
    # Updated URL for 'Get Product By Brand Name'
    url = "https://iherb-product-data-api.p.rapidapi.com/api/IHerb/GetProductByBrandName"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "iherb-product-data-api.p.rapidapi.com"
    }

    # --- API Payload ---
    # Updated payload to search for 'NOW Foods' and request 20 items per page.
    payload = {
        "brandName": "NOW Foods",
        "pageNumber": 1,
        "pageSize": 20 # Request 20 items per page
    }

    send_telegram_message("🔍 בודק 20 מוצרים ראשונים של NOW Foods...")

    # --- Make API Request ---
    try:
        # Added a timeout to prevent indefinite waiting
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

    except requests.exceptions.HTTPError as errh:
        error_msg = f"❌ שגיאת HTTP מה־API ({response.status_code}): {errh}"
        print(error_msg)
        send_telegram_message(error_msg)
        return
    except requests.exceptions.ConnectionError as errc:
        error_msg = f"❌ שגיאת חיבור ל־API: {errc}"
        print(error_msg)
        send_telegram_message(error_msg)
        return
    except requests.exceptions.Timeout as errt:
        error_msg = f"❌ פסק זמן מה־API: {errt}"
        print(error_msg)
        send_telegram_message(error_msg)
        return
    except requests.exceptions.RequestException as err:
        error_msg = f"❌ שגיאה כללית בבקשה ל־API: {err}"
        print(error_msg)
        send_telegram_message(error_msg)
        return

    print("Status Code:", response.status_code)
    print("Response Text (first 500 chars):", response.text[:500]) # Print only part of the text

    # --- Parse JSON Response ---
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        error_msg = f"❌ שגיאה בפענוח JSON מה־API: {e}\nResponse: {response.text}"
        print(error_msg)
        send_telegram_message(error_msg)
        return
    except Exception as e: # Catch any other unexpected errors during JSON parsing
        error_msg = f"❌ שגיאה בלתי צפויה בפענוח JSON: {e}\nResponse: {response.text}"
        print(error_msg)
        send_telegram_message(error_msg)
        return

    # --- Process Products ---
    count = 0
    products_found = data.get("data", [])

    if not products_found:
        send_telegram_message("ℹ️ לא נמצאו מוצרים של NOW Foods כרגע.")
        return

    for item in products_found:
        try:
            title = item.get("productName", "שם לא ידוע")
            price = item.get("salePrice")
            link = item.get("productUrl", "#")

            # Attempt to clean and convert price if it exists
            if price and isinstance(price, str):
                try:
                    price_float = float(price.replace("$", ""))
                    price_display = f"${price_float:.2f}" # Format to 2 decimal places
                except ValueError:
                    price_display = price # Keep as string if conversion fails
            else:
                price_display = "מחיר לא זמין" # Or handle as appropriate

            msg = (
                f"*שם מוצר:* {title}\n"
                f"*מחיר:* {price_display}\n"
                f"[לינק למוצר]({link})"
            )
            send_telegram_message(msg)
            count += 1

            if count >= 20: # Stop after 20 products
                break
        except Exception as e:
            print(f"Error processing product item: {e}. Item data: {item}")
            send_telegram_message(f"⚠️ שגיאה בעיבוד מוצר: {e}")
            continue

    if count == 0:
        send_telegram_message("ℹ️ לא נמצאו מוצרים מתאימים של NOW Foods כרגע.")
    else:
        send_telegram_message(f"✅ נמצאו ופורסמו {count} מוצרים של NOW Foods.")

# --- Script Entry Point ---
if __name__ == "__main__":
    # Basic check for environment variables before running
    if not all([BOT_TOKEN, CHANNEL_ID, RAPIDAPI_KEY]):
        print("Error: One or more required environment variables (BOT_TOKEN, CHANNEL_ID, RAPIDAPI_KEY) are not set.")
        print("Please ensure they are configured in your Railway project or local environment.")
    else:
        fetch_now_foods_products()
