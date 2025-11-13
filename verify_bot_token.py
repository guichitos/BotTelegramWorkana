from telegram import Bot
import asyncio

TOKEN = "8017150739:AAGb1UzPk9mWdY5GIfCh2pwLi6J1_NY4Kvk"

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
