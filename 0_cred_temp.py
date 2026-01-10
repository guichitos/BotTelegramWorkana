"""Temporary storage for credentials removed from source code defaults.

Review and delete this file after confirming all env values are set.
"""

REMOVED_CREDENTIAL_DEFAULTS = {
    "variables_api_db": {
        "host": "127.0.0.1",
        "port": 3306,
        "database": "variables_api",
        "user": "root",
        "password": "",
        "vps_database": "admin_variables_api",
        "vps_user": "admin_variables_user",
        "vps_password": "default-fallback",
    },
    "workana_bot_database_model": {
        "host": "127.0.0.1",
        "port": 3306,
        "database": "proyectos_workana_db",
        "user": "root",
        "password": "",
        "laptop_database": "proyectos_workana_laptop",
        "vps_database": "admin_proyectos_workana",
        "vps_user": "admin_user_proyectos_db",
        "vps_password": "passdeuser_proy_DB_25",
    },
}
