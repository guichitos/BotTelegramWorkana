# workana_url.py
from urllib.parse import urlencode
from typing import Iterable, Optional, List
from user_skills_model import UserSkills  # Usa la clase que ya maneja DB internamente

# Defaults
DEFAULT_SKILLS: List[str] = [
    "arduino",
    "data-entry",
    "data-science",
    "english",
    "industrial-engineering",
    "microsoft-access",
    "microsoft-excel",
    "mysql",
    "php",
    "woocommerce",
    "pc",
]
DEFAULT_LANGUAGE: str = "es"
DEFAULT_QUERY: Optional[str] = None
DEFAULT_PAGE: Optional[int] = None
DEFAULT_SORT: Optional[str] = None

def normalize_skill(s: str) -> str:
    """Normaliza a slug de Workana: minúsculas, trim, espacios -> guiones."""
    return "-".join(s.strip().lower().split())

def build_workana_url(
    user_id: Optional[int] = None,
    language: Optional[str] = None,
    query: Optional[str] = None,
    page: Optional[int] = None,
    sort: Optional[str] = None,
) -> str:
    base = "https://www.workana.com/jobs"

    # Valores por defecto
    language = language or DEFAULT_LANGUAGE
    query    = query if query is not None else DEFAULT_QUERY
    page     = page if page is not None else DEFAULT_PAGE
    sort     = sort if sort is not None else DEFAULT_SORT

    # Intentar leer skills desde la BD
    print(f"[DEBUG] Intentando obtener skills desde BD para user_id={user_id}")
    db_skills: List[str] = []
    try:
        user_skill_list = UserSkills(user_id)
        db_skills = user_skill_list.GetAll() or []
        print(f"[DEBUG] Skills obtenidos desde BD: {db_skills}")
    except Exception as e:
        print(f"[DEBUG] Error al obtener skills desde BD: {e}")
        db_skills = []

    # Determinar qué lista usar
    if db_skills:
        skills = db_skills
        print("[DEBUG] Usando skills desde la BD.")
    else:
        skills = DEFAULT_SKILLS
        print("[DEBUG] Usando DEFAULT_SKILLS porque la BD está vacía o falló.")

    # Normalizar
    skills_clean = [normalize_skill(s) for s in skills if isinstance(s, str) and s.strip()]
    print(f"[DEBUG] Lista final de skills normalizados: {skills_clean}")

    # Armar parámetros
    params = {
        "language": language,
        "skills": ",".join(skills_clean) if skills_clean else None,
        "query": query or None,
        "page": str(page) if isinstance(page, int) else None,
        "sort": sort or None,
    }
    params = {k: v for k, v in params.items() if v is not None}

    url = f"{base}?{urlencode(params)}"
    print(f"[DEBUG] URL generada: {url}")
    return url

if __name__ == "__main__":
    print(build_workana_url(user_id=123456789))
