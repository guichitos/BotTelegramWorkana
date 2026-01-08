# bot_test.py
import asyncio
from typing import cast

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

    class FakeContext:
        pass

    context = cast(ContextTypes.DEFAULT_TYPE, FakeContext())
    await start(FakeUpdate(), context)
    await registrar(FakeUpdate(), context)
    await stop(FakeUpdate(), context)
    await ayuda(FakeUpdate(), context)
    await menu(FakeUpdate(), context)

if __name__ == "__main__":
    asyncio.run(test_basico())
