import html
from urllib.parse import quote

from telegram import Message, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from config_settings import load_settings
from workana_flag_manager import (
    activar_script,
    desactivar_script,
    tiene_conexion_config,
    obtener_codigo_error_conexion,
)
from workana_bot_database_model import WorkanaBotDatabase
from user_model import User
from user_skills_model import UserSkills


def _get_message(update: Update) -> Message | None:
    message = update.effective_message
    if isinstance(message, Message):
        return message
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = _get_message(update)
    if message is None:
        return

    if not tiene_conexion_config():
        await message.reply_text(
            "No se pudo conectar a la base de datos de configuración.\n"
            "Contactá a Servicio Técnico e informá el código de error: "
            f"{obtener_codigo_error_conexion()}."
        )
        return

    if activar_script():
        await message.reply_text(
            "Monitoreo iniciado correctamente.\n"
            "Puedes usar los comandos disponibles para modificar la configuración."
        )
    else:
        await message.reply_text(
            "No se pudo iniciar el monitoreo.\n"
            "Contactá a Servicio Técnico e informá el código de error: "
            f"{obtener_codigo_error_conexion()}."
        )

async def registrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = _get_message(update)
    if message is None:
        return

    TelegramUserID = update.effective_user.id
    TelegramUsername = update.effective_user.username or "sin_usuario"

    Database = WorkanaBotDatabase()
    Database.connect()

    if not Database.IsConnected:
        await message.reply_text("No es posible conectarse a la base de datos.")
        return

    BotUser = User(TelegramUserID, Database)

    if BotUser.IsRegistered:
        await message.reply_text("Ya estás registrado.")
    else:
        settings = load_settings()
        try:
            max_users = int(settings.get("max_users", 1))
        except (TypeError, ValueError):
            max_users = 1

        if max_users <= 0:
            max_users = 1

        usuarios_activos = User.CountActive(Database)
        if usuarios_activos >= max_users:
            await message.reply_text(
                "No hay invitaciones disponibles en este momento. "
                "Pronto se habilitarán más cupos."
            )
            Database.disconnect()
            return

        RegistrationSuccess = BotUser.Register(TelegramUsername)
        if RegistrationSuccess:
            estado = "reactivado" if BotUser.IsActivated else "registrado"
            await message.reply_text(f"Usuario {estado} correctamente.")
        else:
            await message.reply_text("No fue posible registrar el usuario.")

    Database.disconnect()

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = _get_message(update)
    if message is None:
        return

    if not tiene_conexion_config():
        await message.reply_text(
            "No se pudo conectar a la base de datos de configuración.\n"
            "Contactá a Servicio Técnico e informá el código de error: "
            f"{obtener_codigo_error_conexion()}."
        )
        return

    if desactivar_script():
        await message.reply_text("Monitoreo detenido.")
    else:
        await message.reply_text(
            "No se pudo detener el monitoreo.\n"
            "Contactá a Servicio Técnico e informá el código de error: "
            f"{obtener_codigo_error_conexion()}."
        )

async def eliminar_cuenta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = _get_message(update)
    if message is None:
        return

    TelegramUserID = update.effective_user.id

    Database = WorkanaBotDatabase()
    Database.connect()

    if not Database.IsConnected:
        await message.reply_text("No es posible conectarse a la base de datos.")
        return

    usuario = User(TelegramUserID, Database)
    bot_username = update.get_bot().username or ""

    if not usuario.IsRegistered:
        Database.disconnect()
        await message.reply_text("No estás registrado. Usá /registrar para crear tu cuenta.")
        return

    comando_confirmacion = _formatear_comando_enlace(
        "/confirmar_eliminar_cuenta", bot_username
    )
    Database.disconnect()

    await message.reply_text(
        (
            "Vas a eliminar tu cuenta del bot.\n"
            f"Confirmá tocando {comando_confirmacion} o cancelá con /menu.\n"
            "Si no se completa automáticamente, copiá y enviá la línea mostrada."
        ),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def confirmar_eliminar_cuenta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = _get_message(update)
    if message is None:
        return

    TelegramUserID = update.effective_user.id
    bot_username = update.get_bot().username or ""

    mensaje = _eliminar_cuenta_confirmada(TelegramUserID, bot_username)
    await message.reply_text(
        mensaje,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = _get_message(update)
    if message is None:
        return

    mensaje = (
        "Comandos disponibles:\n\n"
        "/registrar - Registrar tu usuario para recibir oportunidades\n"
        "/start - Iniciar el monitoreo de nuevas oportunidades\n"
        "/stop - Detener el monitoreo\n"
        "/borrar - Desactivar tu cuenta de forma segura\n"
        "/habilidades - Ver opciones para administrar tus habilidades\n"
        "/eliminar_cuenta - Eliminar tu cuenta del bot\n"
        "/menu - Mostrar los comandos disponibles en forma de lista"
    )
    await message.reply_text(mensaje)

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = _get_message(update)
    if message is None:
        return

    mensaje = (
        "Menú de opciones:\n"
        "/registrar\n"
        "/habilidades\n"
        "/start\n"
        "/stop\n"
        "/eliminar_cuenta\n"
        "/ayuda"
    )
    await message.reply_text(mensaje)

async def comandos_invalidos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = _get_message(update)
    if message is None:
        return

    await message.reply_text("Comando no reconocido. Usá /ayuda para ver los comandos disponibles.")


async def manejar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data or ""
    TelegramUserID = query.from_user.id

    if not data:
        await query.answer()
        return

    if data.startswith("elim_skill:"):
        skill_slug = data.split(":", 1)[1]
        teclado = _build_confirm_keyboard(
            f"elim_confirm:{skill_slug}", "elim_cancel", "Sí, eliminar", "Cancelar"
        )
        await query.answer()
        await query.message.reply_text(
            f"¿Confirmás eliminar la habilidad: {skill_slug}?", reply_markup=teclado
        )
        return

    if data.startswith("elim_confirm:"):
        skill_slug = data.split(":", 1)[1]
        mensaje = _eliminar_habilidad_confirmada(TelegramUserID, skill_slug)
        await query.answer()
        await query.message.reply_text(mensaje)
        return

    if data == "elim_cancel":
        await query.answer("Operación cancelada")
        Database = WorkanaBotDatabase()
        Database.connect()
        if not Database.IsConnected:
            await query.message.reply_text("No es posible conectarse a la base de datos.")
            Database.disconnect()
            return
        SkillsManager = UserSkills(TelegramUserID, Database)
        estado = _formatear_estado_habilidades(SkillsManager)
        Database.disconnect()
        await query.message.reply_text(f"Cancelaste la eliminación.\n\n{estado}")
        return

    if data == "limpiar_confirm":
        mensaje = _limpiar_habilidades_confirmado(TelegramUserID)
        await query.answer()
        await query.message.reply_text(mensaje)
        return

    if data == "limpiar_cancel":
        await query.answer("Operación cancelada")
        Database = WorkanaBotDatabase()
        Database.connect()
        if not Database.IsConnected:
            await query.message.reply_text("No es posible conectarse a la base de datos.")
            Database.disconnect()
            return
        SkillsManager = UserSkills(TelegramUserID, Database)
        estado = _formatear_estado_habilidades(SkillsManager)
        Database.disconnect()
        await query.message.reply_text(f"Cancelaste la limpieza.\n\n{estado}")
        return

    await query.answer()

async def habilidades(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = _get_message(update)
    if message is None:
        return

    TelegramUserID = update.effective_user.id

    Database = WorkanaBotDatabase()
    Database.connect()

    if not Database.IsConnected:
        await message.reply_text("No es posible conectarse a la base de datos.")
        return

    SkillsManager = UserSkills(TelegramUserID, Database)
    mensaje = _formatear_estado_habilidades(SkillsManager)

    await message.reply_text(mensaje)
    Database.disconnect()


async def agregar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = _get_message(update)
    if message is None:
        return

    TelegramUserID = update.effective_user.id
    skill = " ".join(context.args).strip()

    if not skill:
        await message.reply_text(
            "Indica la habilidad que querés agregar: /agregar <habilidad>."
        )
        return

    Database = WorkanaBotDatabase()
    Database.connect()

    if not Database.IsConnected:
        await message.reply_text("No es posible conectarse a la base de datos.")
        return

    SkillsManager = UserSkills(TelegramUserID, Database)
    if not SkillsManager.is_registered:
        Database.disconnect()
        await message.reply_text(
            "No estás registrado. Usá /registrar para crear tu cuenta antes de agregar habilidades."
        )
        return
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
    await message.reply_text(f"{mensaje}\n\n{estado_habilidades}")


async def eliminar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = _get_message(update)
    if message is None:
        return

    TelegramUserID = update.effective_user.id
    skill = " ".join(context.args).strip()

    Database = WorkanaBotDatabase()
    Database.connect()

    if not Database.IsConnected:
        await message.reply_text("No es posible conectarse a la base de datos.")
        return

    SkillsManager = UserSkills(TelegramUserID, Database)
    habilidades_actuales = SkillsManager.GetAll()

    if not skill:
        if not habilidades_actuales:
            estado_habilidades = _formatear_estado_habilidades(SkillsManager)
            await message.reply_text(estado_habilidades)
        else:
            bot_username = update.get_bot().username or ""
            comandos = "\n".join(
                _formatear_comando_enlace(f"/eliminar_habilidad {s}", bot_username)
                for s in habilidades_actuales
            )
            await message.reply_text(
                (
                    "Elegí qué habilidad querés eliminar tocando uno de estos enlaces:\n"
                    f"{comandos}\n\n"
                    "Si no se completa automáticamente, copiá y enviá la línea mostrada.\n"
                    "Se pedirá confirmación antes de borrar."
                ),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )

        Database.disconnect()
        return

    skill_slug = SkillsManager.normalize_skill(skill)

    if not SkillsManager.HasSkill(skill_slug):
        mensaje = "La habilidad indicada no está registrada."
    else:
        bot_username = update.get_bot().username or ""
        comando_confirmacion = _formatear_comando_enlace(
            f"/confirmar_eliminar_habilidad {skill_slug}", bot_username
        )

        Database.disconnect()
        await message.reply_text(
            (
                f"Vas a eliminar la habilidad: {skill_slug}.\n"
                f"Confirmá tocando {comando_confirmacion} o cancelá con /habilidades.\n"
                "Si no se completa automáticamente, copiá y enviá la línea mostrada."
            ),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        return

    estado_habilidades = _formatear_estado_habilidades(SkillsManager)

    Database.disconnect()
    await message.reply_text(f"{mensaje}\n\n{estado_habilidades}")


async def limpiar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = _get_message(update)
    if message is None:
        return

    TelegramUserID = update.effective_user.id

    Database = WorkanaBotDatabase()
    Database.connect()

    if not Database.IsConnected:
        await message.reply_text("No es posible conectarse a la base de datos.")
        return

    SkillsManager = UserSkills(TelegramUserID, Database)
    habilidades_actuales = SkillsManager.GetAll()

    if not habilidades_actuales:
        mensaje = "No tenés habilidades para limpiar."
    else:
        Database.disconnect()
        await message.reply_text(
            (
                "Vas a eliminar todas tus habilidades. ¿Confirmás?\n"
                "Esta acción no se puede deshacer.\n\n"
                "Enviá /confirmar_limpiar para continuar o /habilidades para cancelar."
            )
        )
        return

    estado_habilidades = _formatear_estado_habilidades(SkillsManager)

    Database.disconnect()
    await message.reply_text(f"{mensaje}\n\n{estado_habilidades}")


async def confirmar_eliminar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = _get_message(update)
    if message is None:
        return

    TelegramUserID = update.effective_user.id
    skill = " ".join(context.args).strip()

    if not skill:
        await message.reply_text(
            "Indica la habilidad a eliminar: /confirmar_eliminar_habilidad <habilidad>.\n"
            "Para ver tus opciones usá /eliminar_habilidad."
        )
        return

    mensaje = _eliminar_habilidad_confirmada(TelegramUserID, skill)
    await message.reply_text(mensaje)


async def confirmar_limpiar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = _get_message(update)
    if message is None:
        return

    TelegramUserID = update.effective_user.id
    mensaje = _limpiar_habilidades_confirmado(TelegramUserID)
    await message.reply_text(mensaje)


def _eliminar_cuenta_confirmada(user_id: int, bot_username: str) -> str:
    Database = WorkanaBotDatabase()
    Database.connect()

    if not Database.IsConnected:
        Database.disconnect()
        return "No es posible conectarse a la base de datos."

    usuario = User(user_id, Database)
    SkillsManager = UserSkills(user_id, Database)

    if not usuario.IsRegistered:
        mensaje = "No estás registrado. Usá /registrar para crear tu cuenta."
    else:
        habilidades_borradas = SkillsManager.ClearAll()
        borrado = habilidades_borradas and usuario.Delete()
        if borrado:
            mensaje = (
                "Tu cuenta fue eliminada del bot.\n"
                "Si querés volver a usarlo, tendrás que registrarte nuevamente con /registrar."
            )
        else:
            mensaje = "No se pudo borrar la cuenta. Intentá nuevamente más tarde."

    Database.disconnect()
    return mensaje


def _formatear_comando_enlace(comando: str, bot_username: str) -> str:
    comando_visible = html.escape(comando)

    if bot_username:
        comando_encoded = quote(comando)
        return (
            f"<a href=\"https://t.me/{bot_username}?text={comando_encoded}\">"
            f"{comando_visible}</a>"
        )

    return comando_visible


def _formatear_estado_habilidades(skills_manager: UserSkills) -> str:
    habilidades_actuales = skills_manager.GetAll()

    if habilidades_actuales:
        lista = "\n".join(f"- {s}" for s in habilidades_actuales)
        mensaje = f"Tus habilidades actuales son:\n{lista}"
    else:
        mensaje = "No tienes habilidades registradas."

    mensaje += "\n\nOpciones:\n/agregar\n/eliminar_habilidad\n/limpiar\n/menu"
    return mensaje


def _eliminar_habilidad_confirmada(user_id: int, skill_slug: str) -> str:
    Database = WorkanaBotDatabase()
    Database.connect()

    if not Database.IsConnected:
        Database.disconnect()
        return "No es posible conectarse a la base de datos."

    SkillsManager = UserSkills(user_id, Database)

    if not SkillsManager.HasSkill(skill_slug):
        mensaje = "La habilidad indicada no está registrada."
    else:
        eliminado = SkillsManager.Remove(skill_slug)
        if eliminado:
            mensaje = f"Habilidad eliminada: {skill_slug}."
        else:
            mensaje = "No se pudo eliminar la habilidad. Intentá nuevamente más tarde."

    estado = _formatear_estado_habilidades(SkillsManager)
    Database.disconnect()
    return f"{mensaje}\n\n{estado}"


def _limpiar_habilidades_confirmado(user_id: int) -> str:
    Database = WorkanaBotDatabase()
    Database.connect()

    if not Database.IsConnected:
        Database.disconnect()
        return "No es posible conectarse a la base de datos."

    SkillsManager = UserSkills(user_id, Database)
    habilidades_actuales = SkillsManager.GetAll()

    if not habilidades_actuales:
        mensaje = "No tenés habilidades para limpiar."
    else:
        eliminado = SkillsManager.ClearAll()
        if eliminado:
            mensaje = f"Se limpiaron {len(habilidades_actuales)} habilidades."
        else:
            mensaje = "No se pudieron limpiar las habilidades. Intentá nuevamente más tarde."

    estado = _formatear_estado_habilidades(SkillsManager)
    Database.disconnect()
    return f"{mensaje}\n\n{estado}"
