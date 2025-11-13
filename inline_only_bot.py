# bot_inline.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

from local_o_vps import entorno
from workana_bot_database_model import WorkanaBotDatabase
from workana_flag_manager import activar_script, desactivar_script
from user_model import User

TOKEN = "8017150739:AAGb1UzPk9mWdY5GIfCh2pwLi6J1_NY4Kvk"


# Mostrar menú principal
async def inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Iniciar script", callback_data="start_script")],
        [InlineKeyboardButton("Registrar usuario", callback_data="registrar_usuario")],
        [InlineKeyboardButton("Detener script", callback_data="stop_script")],
        [InlineKeyboardButton("Ayuda", callback_data="mostrar_ayuda")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🤖 *Bienvenido. ¿Qué deseas hacer?*", reply_markup=reply_markup, parse_mode="Markdown")


# Manejador de botones
async def manejar_opciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    username = query.from_user.username or "sin_usuario"

    # Conexión a BD si se necesita
    db = WorkanaBotDatabase()
    db.connect()

    if data == "start_script":
        activar_script(entorno)
        await query.edit_message_text("✅ Script Workana activado.")

    elif data == "stop_script":
        desactivar_script(entorno)
        await query.edit_message_text("⏹️ Script detenido desde Telegram.")

    elif data == "registrar_usuario":
        if not db.IsConnected:
            await query.edit_message_text("❌ No se pudo conectar a la base de datos.")
            return

        bot_user = User(user_id, db)

        if bot_user.IsRegistered:
            await query.edit_message_text("⚠️ Ya estás registrado.")
        else:
            if bot_user.Register(username):
                await query.edit_message_text("✅ Usuario registrado correctamente.")
            else:
                await query.edit_message_text("❌ No fue posible registrar al usuario.")

    elif data == "mostrar_ayuda":
        await query.edit_message_text(
            "*Opciones disponibles:*\n"
            "- Iniciar script Workana\n"
            "- Registrar usuario\n"
            "- Detener script\n"
            "- Ver ayuda\n",
            parse_mode="Markdown"
        )

    else:
        await query.edit_message_text("❓ Opción no reconocida.")

    db.disconnect()


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", inicio))  # solo se usa /start
    app.add_handler(CallbackQueryHandler(manejar_opciones))

    print("🤖 Bot inline iniciado.")
    app.run_polling()


if __name__ == "__main__":
    main()
