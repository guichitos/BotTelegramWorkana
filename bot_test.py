# bot_test.py
import asyncio
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

    await start(FakeUpdate(), FakeContext())
    await registrar(FakeUpdate(), FakeContext())
    await stop(FakeUpdate(), FakeContext())
    await ayuda(FakeUpdate(), FakeContext())
    await menu(FakeUpdate(), FakeContext())

if __name__ == "__main__":
    asyncio.run(test_basico())
