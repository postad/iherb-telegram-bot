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
    Fetches the first 20 products from the specified brand using the
    RapidAPI iHerb 'GET /brands/{brandName}/products' endpoint and sends them
    to a Telegram channel.
    """
    # --- API Endpoint and Headers ---
    # Corrected URL for 'GET /brands/{brandName}/products'
    # The brand name is now part of the URL path.
    brand_name = "100-pure" # Changed brand name to "100-pure"
    url = f"https://iherb-product-data-api.p.rapidapi.com/api/IHerb/brands/{brand_name}/products"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "iherb-product-data-api.p.rapidapi.com"
    }

    # --- API Query Parameters ---
    # Pagination parameters for a GET request are typically in 'params'
    params = {
        "page": 1,        # Corresponds to pageNumber
        "pageSize": 20    # Corresponds to pageSize
    }

    send_telegram_message(f"🔍 בודק 20 מוצרים ראשונים של {brand_name}...")

    # --- Make API Request (now a GET request) ---
    try:
        # Changed to requests.get and passed params instead of json=payload
        response = requests.get(url, headers=headers, params=params, timeout=15)
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
    # The API documentation (Source 1.1) suggests the product list might be under a 'products' key,
    # not 'data'. Let's adjust to check both, with 'products' as primary.
    products_found = data.get("products", data.get("data", []))

    if not products_found:
        send_telegram_message(f"ℹ️ לא נמצאו מוצרים של {brand_name} כרגע.")
        return

    for item in products_found:
        try:
            title = item.get("title", "שם לא ידוע") # Documentation shows 'title' not 'productName'
            price = item.get("price") # Documentation shows 'price' not 'salePrice'
            link = item.get("link", "#") # Documentation shows 'link' not 'productUrl'

            # Attempt to clean and convert price if it exists
            if price is not None: # Price could be float or string from API
                if isinstance(price, str):
                    try:
                        price_float = float(price.replace("$", ""))
                        price_display = f"${price_float:.2f}" # Format to 2 decimal places
                    except ValueError:
                        price_display = price # Keep as string if conversion fails
                else: # Assume it's already a number (int/float)
                    price_display = f"${price:.2f}"
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
        send_telegram_message(f"ℹ️ לא נמצאו מוצרים מתאימים של {brand_name} כרגע.")
    else:
        send_telegram_message(f"✅ נמצאו ופורסמו {count} מוצרים של {brand_name}.")

# --- Script Entry Point ---
if __name__ == "__main__":
    # Basic check for environment variables before running
    if not all([BOT_TOKEN, CHANNEL_ID, RAPIDAPI_KEY]):
        print("Error: One or more required environment variables (BOT_TOKEN, CHANNEL_ID, RAPIDAPI_KEY) are not set.")
        print("Please ensure they are configured in your Railway project or local environment.")
    else:
        fetch_now_foods_products()
