# verify_bot_token.py
import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Token from environment variables
TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN") or ""

if not TOKEN:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN in .env file")

async def main():
    bot = Bot(token=TOKEN)
    me = await bot.get_me()

    print(f"ID: {me.id}")
    print(f"First Name: {me.first_name}")
    print(f"Username: @{me.username}")
    print(f"Is Bot: {me.is_bot}")
    print(f"Can Join Groups: {me.can_join_groups}")
    print(f"Can Read All Group Messages: {me.can_read_all_group_messages}")
    print(f"Supports Inline Queries: {me.supports_inline_queries}")
    print(f"Can Connect to Business: {me.can_connect_to_business}")
    print(f"Has Main Web App: {me.has_main_web_app}")

asyncio.run(main())
