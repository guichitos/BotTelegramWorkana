# handlers_test.py
import asyncio
from typing import cast

from telegram import Update
from telegram.ext import ContextTypes

from handlers import start, registrar, stop, ayuda, menu

class FakeUser:
    id = 123456789
    username = "usuario_prueba"

class FakeMessage:
    async def reply_text(self, text, **kwargs):
        print(f"[BOT] {text}")

class FakeUpdate:
    effective_user = FakeUser()
    message = FakeMessage()
    effective_message = message

class FakeContext:
    pass

async def test_all():
    print(">> Ejecutando test_all...")
    update = cast(Update, FakeUpdate())
    context = cast(ContextTypes.DEFAULT_TYPE, FakeContext())
    for label, func in [
        ("start", start),
        ("registrar", registrar),
        ("stop", stop),
        ("ayuda", ayuda),
        ("menu", menu),
    ]:
        print(f"\n>> Probando /{label}")
        await func(update, context)
    print("✅ test_all finalizado.")

if __name__ == "__main__":
    asyncio.run(test_all())
