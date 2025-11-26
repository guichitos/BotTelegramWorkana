# bot.py
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from handlers import (
    start, registrar, stop, ayuda, menu,
    habilidades, agregar, eliminar, limpiar,
    comandos_invalidos
)

TOKEN = "8017150739:AAGb1UzPk9mWdY5GIfCh2pwLi6J1_NY4Kvk"

def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("registrar", registrar))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CommandHandler("habilidades", habilidades))
    app.add_handler(CommandHandler("agregar", agregar))
    app.add_handler(CommandHandler("eliminar", eliminar))
    app.add_handler(CommandHandler("limpiar", limpiar))
    app.add_handler(MessageHandler(filters.COMMAND, comandos_invalidos))

    print("Bot iniciado. Esperando comandos...")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
