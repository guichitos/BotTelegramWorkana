# bot_test.py
import asyncio
from typing import cast

from telegram import Update
from telegram.ext import ContextTypes

from handlers import start, registrar, stop, ayuda, menu

async def test_basico():
    class FakeUser:
        id = 1
        username = "test_user"

    class FakeMessage:
        async def reply_text(self, text, **kwargs):
            print(f"[BOT] {text}")

    class FakeUpdate:
        effective_user = FakeUser()
        message = FakeMessage()
        effective_message = message

    class FakeContext:
        pass

    context = cast(ContextTypes.DEFAULT_TYPE, FakeContext())
    update = cast(Update, FakeUpdate())
    await start(update, context)
    await registrar(update, context)
    await stop(update, context)
    await ayuda(update, context)
    await menu(update, context)

if __name__ == "__main__":
    asyncio.run(test_basico())
