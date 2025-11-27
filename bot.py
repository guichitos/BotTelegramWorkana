# bot.py
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from handlers import (
    start,
    registrar,
    stop,
    ayuda,
    menu,
    eliminar_cuenta,
    habilidades,
    agregar,
    eliminar,
    limpiar,
    confirmar_eliminar,
    confirmar_limpiar,
    confirmar_eliminar_cuenta,
    comandos_invalidos,
)

TOKEN = "8017150739:AAGb1UzPk9mWdY5GIfCh2pwLi6J1_NY4Kvk"

def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("registrar", registrar))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CommandHandler(["eliminar_cuenta", "borrar"], eliminar_cuenta))
    app.add_handler(CommandHandler("habilidades", habilidades))
    app.add_handler(CommandHandler("agregar", agregar))
    app.add_handler(CommandHandler("eliminar", eliminar))
    app.add_handler(CommandHandler("limpiar", limpiar))
    app.add_handler(CommandHandler("confirmar_eliminar", confirmar_eliminar))
    app.add_handler(CommandHandler("confirmar_limpiar", confirmar_limpiar))
    app.add_handler(CommandHandler(["confirmar_eliminar_cuenta", "confirmar_borrar"], confirmar_eliminar_cuenta))
    app.add_handler(MessageHandler(filters.COMMAND, comandos_invalidos))

    print("Bot iniciado. Esperando comandos...")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
