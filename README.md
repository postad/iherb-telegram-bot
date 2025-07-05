# iHerb Telegram Bot

This bot scrapes probiotic products from iHerb every 3 hours,
filters GMP certified (non-Chinese) products, and posts them to a Telegram channel.

## Environment Variables (to set on Railway)
- `BOT_TOKEN`: Your Telegram bot token
- `CHANNEL_ID`: Your Telegram channel ID (e.g., `@rakbriut`)

## Run locally
```bash
pip install -r requirements.txt
python bot.py
```
