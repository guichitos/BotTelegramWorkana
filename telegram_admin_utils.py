from typing import Optional

from dotenv import load_dotenv

from workana_bot_database_model import WorkanaBotDatabase

load_dotenv()


def get_admin_chat_id() -> Optional[int]:
    """Return the telegram_user_id for the admin user in bot_users."""
    db = WorkanaBotDatabase()
    query = (
        "SELECT telegram_user_id FROM bot_users "
        "WHERE role = 'admin' ORDER BY id ASC LIMIT 1"
    )
    result = db.execute_scalar(query)
    if result is None:
        return None
    return int(result)
