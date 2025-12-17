# projects_db_manager.py
from typing import List, Optional
from datetime import datetime
from projects_db import proyectosDatabase
from models import Project
from send_telegram_message import mensaje as send_telegram_message
from workana_bot_database_model import WorkanaBotDatabase

class ProjectRepository:
    def __init__(self):
        self._db = proyectosDatabase()
        self._bot_db = WorkanaBotDatabase()

    @staticmethod
    def _normalize_skill_value(value: str) -> str:
        return "-".join(value.strip().lower().split()) if value else ""

    def _collect_project_skill_slugs(self, skills) -> set[str]:
        normalized: set[str] = set()
        for skill in skills or []:
            slug = self._normalize_skill_value(skill.get("slug", "")) if isinstance(skill, dict) else ""
            name = self._normalize_skill_value(skill.get("name", "")) if isinstance(skill, dict) else ""
            if slug:
                normalized.add(slug)
            if name:
                normalized.add(name)
            if name:
                normalized.add(name.replace("-", " "))
        return normalized

    def _get_user_skill_map(self) -> dict[int, list[str]]:
        query = (
            "SELECT u.telegram_user_id, us.skill_slug "
            "FROM user_skills us "
            "JOIN bot_users u ON us.user_id = u.id "
            "WHERE u.active = TRUE"
        )
        rows = self._bot_db.execute_query(query)
        skills_by_user: dict[int, list[str]] = {}
        for telegram_user_id, skill_slug in rows:
            if telegram_user_id is None or skill_slug is None:
                continue
            normalized = self._normalize_skill_value(str(skill_slug))
            if not normalized:
                continue
            skills_by_user.setdefault(int(telegram_user_id), []).append(normalized)
        return skills_by_user

    def _match_users_by_skills(self, project_skills) -> dict[int, list[str]]:
        project_skill_set = self._collect_project_skill_slugs(project_skills)
        if not project_skill_set:
            return {}

        user_skills_map = self._get_user_skill_map()
        matches: dict[int, list[str]] = {}
        for user_id, skills in user_skills_map.items():
            overlap = sorted(project_skill_set.intersection(skills))
            if overlap:
                matches[user_id] = overlap
        return matches

    def SaveProjects(self, projects: List[Project]) -> int:
        inserted = 0
        for p in projects:
            was_existing = self._db.proyecto_exists_by_url(p.Url)
            ok_id = self._db.upsert_by_url(
                title=p.Title,
                url=p.Url,
                description=p.Description,
                posted_at=None if was_existing else datetime.now()
            )
            if ok_id:
                inserted += 1
                if p.Skills:
                    try:
                        self._db.replace_project_skills(ok_id, p.Skills)
                    except Exception as ex:
                        print(f"Error guardando skills para proyecto {ok_id}: {ex}")
        return inserted

    def notify_users_for_projects(self, projects: List[dict]) -> None:
        """Send Telegram alerts for provided projects based on skill overlaps."""
        user_skill_map = self._get_user_skill_map()
        if not user_skill_map:
            print("[NOTIFY] No hay usuarios activos con skills configuradas.")
            return

        for project in projects:
            pid = project.get("id")
            skills = project.get("skills", [])
            matches = self._match_users_by_skills(skills)
            if not matches:
                print(f"[NOTIFY] Proyecto {pid} sin usuarios con skills coincidentes.")
                continue

            title = project.get("title", "(Sin título)")
            url = project.get("url", "")
            for chat_id, matched_skills in matches.items():
                try:
                    send_telegram_message(title, url, chat_id=chat_id, matched_skills=matched_skills)
                except Exception as ex:
                    print(
                        f"Error enviando mensaje a Telegram para usuario {chat_id} "
                        f"en proyecto {pid}: {ex}"
                    )

    def get_projects_for_skill_scan(self, since: Optional[datetime], limit: int = 200) -> List[dict]:
        """Retrieve projects and skills to evaluate against user profiles."""
        return self._db.get_projects_with_skills_since(since=since, limit=limit)
    
if __name__ == "__main__":
    repo = ProjectRepository()

    # Creamos datos ficticios para probar inserción
    test_projects = [
        Project(
            Title="Proyecto de prueba 1",
            Description="Descripción de prueba uno",
            Url="https://www.workana.com/job/test1"
        ),
        Project(
            Title="Proyecto de prueba 2",
            Description="Descripción de prueba dos",
            Url="https://www.workana.com/job/test2"
        )
    ]

    print("Probando inserción de proyectos de prueba...")
    inserted_count = repo.SaveProjects(test_projects)
    print(f"✅ Proyectos insertados/actualizados: {inserted_count}")