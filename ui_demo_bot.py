# ui_demo_bot.py
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    ForceReply,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = "8017150739:AAGb1UzPk9mWdY5GIfCh2pwLi6J1_NY4Kvk"


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bienvenido. Comandos disponibles:\n"
        "/inline - Probar InlineKeyboardMarkup\n"
        "/reply - Probar ReplyKeyboardMarkup\n"
        "/force - Probar ForceReply\n"
        "/ocultar - Ocultar teclado personalizado"
    )


# /inline
async def inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔘 Botón inline A", callback_data="inline_a")],
        [InlineKeyboardButton("🌐 Abrir Google", url="https://www.google.com")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🟢 Este es un *InlineKeyboardMarkup*:", reply_markup=markup, parse_mode="Markdown")


# /reply
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["✔️ Sí", "❌ No"], ["❓ Tal vez"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("🟡 Este es un *ReplyKeyboardMarkup*:", reply_markup=markup, parse_mode="Markdown")


# /force
async def force(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔵 Este es un *ForceReply*:", reply_markup=ForceReply(), parse_mode="Markdown")


# /ocultar
async def ocultar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚪ Teclado personalizado ocultado.", reply_markup=ReplyKeyboardRemove())


# Callback para botones inline
async def manejar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "inline_a":
        await query.edit_message_text("✅ Pulsaste el botón inline A.")
    else:
        await query.edit_message_text("❓ Callback no reconocido.")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("inline", inline))
    app.add_handler(CommandHandler("reply", reply))
    app.add_handler(CommandHandler("force", force))
    app.add_handler(CommandHandler("ocultar", ocultar))
    app.add_handler(CallbackQueryHandler(manejar_callback))

    print("🧪 Bot de prueba de UI iniciado.")
    app.run_polling()


if __name__ == "__main__":
    main()
