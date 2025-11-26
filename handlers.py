from telegram import Update
from telegram.ext import ContextTypes
from workana_flag_manager import (
    activar_script,
    desactivar_script,
    tiene_conexion_config,
    obtener_codigo_error_conexion,
)
from workana_bot_database_model import WorkanaBotDatabase
from user_model import User
from user_skills_model import UserSkills


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_conexion_config():
        await update.message.reply_text(
            "No se pudo conectar a la base de datos de configuración.\n"
            "Contactá a Servicio Técnico e informá el código de error: "
            f"{obtener_codigo_error_conexion()}."
        )
        return

    if activar_script():
        await update.message.reply_text(
            "Monitoreo iniciado correctamente.\n"
            "Puedes usar los comandos disponibles para modificar la configuración."
        )
    else:
        await update.message.reply_text(
            "No se pudo iniciar el monitoreo.\n"
            "Contactá a Servicio Técnico e informá el código de error: "
            f"{obtener_codigo_error_conexion()}."
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
    if not tiene_conexion_config():
        await update.message.reply_text(
            "No se pudo conectar a la base de datos de configuración.\n"
            "Contactá a Servicio Técnico e informá el código de error: "
            f"{obtener_codigo_error_conexion()}."
        )
        return

    if desactivar_script():
        await update.message.reply_text("Monitoreo detenido.")
    else:
        await update.message.reply_text(
            "No se pudo detener el monitoreo.\n"
            "Contactá a Servicio Técnico e informá el código de error: "
            f"{obtener_codigo_error_conexion()}."
        )

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
    mensaje = _formatear_estado_habilidades(SkillsManager)

    await update.message.reply_text(mensaje)
    Database.disconnect()


async def agregar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    TelegramUserID = update.effective_user.id
    skill = " ".join(context.args).strip()

    if not skill:
        await update.message.reply_text(
            "Indica la habilidad que querés agregar: /agregar <habilidad>."
        )
        return

    Database = WorkanaBotDatabase()
    Database.connect()

    if not Database.IsConnected:
        await update.message.reply_text("No es posible conectarse a la base de datos.")
        return

    SkillsManager = UserSkills(TelegramUserID, Database)
    skill_slug = SkillsManager.normalize_skill(skill)

    if SkillsManager.HasSkill(skill):
        mensaje = f"La habilidad ya estaba registrada: {skill_slug}."
    else:
        agregado = SkillsManager.Add(skill)
        if agregado:
            mensaje = f"Habilidad agregada: {skill_slug}."
        else:
            mensaje = "No se pudo agregar la habilidad. Intentá nuevamente más tarde."

    estado_habilidades = _formatear_estado_habilidades(SkillsManager)

    Database.disconnect()
    await update.message.reply_text(f"{mensaje}\n\n{estado_habilidades}")


async def eliminar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    TelegramUserID = update.effective_user.id
    skill = " ".join(context.args).strip()

    if not skill:
        await update.message.reply_text(
            "Indica la habilidad que querés eliminar: /eliminar <habilidad>."
        )
        return

    Database = WorkanaBotDatabase()
    Database.connect()

    if not Database.IsConnected:
        await update.message.reply_text("No es posible conectarse a la base de datos.")
        return

    SkillsManager = UserSkills(TelegramUserID, Database)
    skill_slug = SkillsManager.normalize_skill(skill)

    if not SkillsManager.HasSkill(skill):
        mensaje = "La habilidad indicada no está registrada."
    else:
        eliminado = SkillsManager.Remove(skill)
        if eliminado:
            mensaje = f"Habilidad eliminada: {skill_slug}."
        else:
            mensaje = "No se pudo eliminar la habilidad. Intentá nuevamente más tarde."

    estado_habilidades = _formatear_estado_habilidades(SkillsManager)

    Database.disconnect()
    await update.message.reply_text(f"{mensaje}\n\n{estado_habilidades}")


async def limpiar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    TelegramUserID = update.effective_user.id

    Database = WorkanaBotDatabase()
    Database.connect()

    if not Database.IsConnected:
        await update.message.reply_text("No es posible conectarse a la base de datos.")
        return

    SkillsManager = UserSkills(TelegramUserID, Database)
    habilidades_actuales = SkillsManager.GetAll()

    if not habilidades_actuales:
        mensaje = "No tenés habilidades para limpiar."
    else:
        eliminado = SkillsManager.ClearAll()
        if eliminado:
            mensaje = f"Se limpiaron {len(habilidades_actuales)} habilidades."
        else:
            mensaje = "No se pudieron limpiar las habilidades. Intentá nuevamente más tarde."

    estado_habilidades = _formatear_estado_habilidades(SkillsManager)

    Database.disconnect()
    await update.message.reply_text(f"{mensaje}\n\n{estado_habilidades}")


def _formatear_estado_habilidades(skills_manager: UserSkills) -> str:
    habilidades_actuales = skills_manager.GetAll()

    if habilidades_actuales:
        lista = "\n".join(f"- {s}" for s in habilidades_actuales)
        mensaje = f"Tus habilidades actuales son:\n{lista}"
    else:
        mensaje = "No tienes habilidades registradas."

    mensaje += "\n\nOpciones:\n/agregar\n/eliminar\n/limpiar"
    return mensaje

