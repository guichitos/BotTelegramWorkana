# test_bot.py
import asyncio
from typing import cast

from telegram import Update
from telegram.ext import ContextTypes

from handlers import start, registrar, stop, ayuda, menu

async def test_basico():
    print(">> Ejecutando test_basico...")
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
    actions = [
        ("/start", start),
        ("/registrar", registrar),
        ("/stop", stop),
        ("/ayuda", ayuda),
        ("/menu", menu),
    ]

    for command, handler in actions:
        print(f"Ejecutando {command}...")
        await handler(update, context)
        print(f"✅ {command} ejecutado correctamente.")

    print("✅ test_basico finalizado. Comandos verificados: /start, /registrar, /stop, /ayuda, /menu")

if __name__ == "__main__":
    asyncio.run(test_basico())
