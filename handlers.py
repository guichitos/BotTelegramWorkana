from telegram import Update
from telegram.ext import ContextTypes
from workana_flag_manager import activar_script, desactivar_script
from workana_bot_database_model import WorkanaBotDatabase
from user_model import User
from user_skills import UserSkills


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    activar_script()
    await update.message.reply_text(
        "Monitoreo iniciado correctamente.\nPuedes usar los comandos disponibles para modificar la configuración."
    )

async def registrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    TelegramUserID = update.effective_user.id
    TelegramUsername = update.effective_user.username or "sin_usuario"

    Database = WorkanaBotDatabase()
    Database.connect()

    if not Database.IsConnected:
        await update.message.reply_text("No es posible conectarse a la base de datos.")
        return

    BotUser = User(TelegramUserID, Database)

    if BotUser.IsRegistered:
        await update.message.reply_text("Ya estás registrado.")
    else:
        RegistrationSuccess = BotUser.Register(TelegramUsername)
        if RegistrationSuccess:
            await update.message.reply_text("Usuario registrado correctamente.")
        else:
            await update.message.reply_text("No fue posible registrar el usuario.")

    Database.disconnect()

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    desactivar_script()
    await update.message.reply_text("Monitoreo detenido.")

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (
        "Comandos disponibles:\n\n"
        "/registrar - Registrar tu usuario para recibir oportunidades\n"
        "/start - Iniciar el monitoreo de nuevas oportunidades\n"
        "/stop - Detener el monitoreo\n"
        "/habilidades - Ver opciones para administrar tus habilidades\n"
        "/menu - Mostrar los comandos disponibles en forma de lista"
    )
    await update.message.reply_text(mensaje)

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (
        "Menú de opciones:\n"
        "/registrar\n"
        "/start\n"
        "/stop\n"
        "/habilidades\n"
        "/ayuda"
    )
    await update.message.reply_text(mensaje)

async def comandos_invalidos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Comando no reconocido. Usá /ayuda para ver los comandos disponibles.")

async def habilidades(update: Update, context: ContextTypes.DEFAULT_TYPE):
    TelegramUserID = update.effective_user.id

    Database = WorkanaBotDatabase()
    Database.connect()

    if not Database.IsConnected:
        await update.message.reply_text("No es posible conectarse a la base de datos.")
        return

    SkillsManager = UserSkills(TelegramUserID, Database)
    habilidades_actuales = SkillsManager.GetAll()

    if habilidades_actuales:
        lista = "\n".join(f"- {s}" for s in habilidades_actuales)
        mensaje = f"Tus habilidades actuales son:\n{lista}"
    else:
        mensaje = "No tienes habilidades registradas."

    mensaje += "\n\nOpciones:\n/agregar_habilidad\n/eliminar_habilidad\n/limpiar_habilidades"

    await update.message.reply_text(mensaje)
    Database.disconnect()

