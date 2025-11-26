"""Compatibilidad: re-exporta el modelo principal de skills.

El archivo real del modelo es `user_skills_model.py`, pero mantenemos este
módulo como alias para no romper importaciones existentes.
"""

from user_skills_model import UserSkills, DEFAULT_USER_ID  # noqa: F401
