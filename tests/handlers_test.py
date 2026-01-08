# handlers_test.py
import asyncio
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

class FakeContext:
    pass

async def test_all():
    update, context = FakeUpdate(), FakeContext()
    for label, func in [
        ("start", start),
        ("registrar", registrar),
        ("stop", stop),
        ("ayuda", ayuda),
        ("menu", menu),
    ]:
        print(f"\n>> Probando /{label}")
        await func(update, context)

if __name__ == "__main__":
    asyncio.run(test_all())
