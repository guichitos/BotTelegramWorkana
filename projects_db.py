# monitor_workana/projects_db.py
"""
ProjectsDatabase: access layer for the Workana projects schema using English table
and column names.

__init__ : Inicializa el manager usando WorkanaBotDatabase y garantiza la
            existencia de la tabla y un usuario por defecto.
ensure_schema : Crea la tabla 'projects' si no existe.
ensure_default_user : Crea un usuario en bot_users para cumplir el FK de
                      projects.user_id si no existe.
_to_dict_row : Convierte una fila (tuple) en un diccionario con claves
               id/user_id/posted_at/title/description/url.
project_exists_by_url : Verifica si existe al menos un registro con la misma url.
insert_project : Inserta un proyecto (user_id, posted_at, title, description, url)
                 y devuelve su ID o None.
upsert_by_url : Si existe un registro con esa url, lo actualiza; si no, inserta;
                devuelve el ID afectado.
update_by_id : Actualiza solo los campos provistos del proyecto indicado por ID.
delete_by_id : Elimina físicamente el registro indicado por ID.
get_recent : Obtiene los registros más recientes ordenados por posted_at (NULL al
             final) e ID.
get_by_url : Devuelve el último registro que coincide con la url (o None si no hay).
bulk_insert : Inserta múltiples proyectos omitiendo los que no tengan title o url.
__main__ : Prueba rápida: conexión/lectura, upsert, actualización, listado y
           borrado del registro de prueba.
"""

import os
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from workana_bot_database_model import WorkanaBotDatabase
from user_skills_model import DEFAULT_USER_ID


class proyectosDatabase:
    """
    Minimal controller for the English 'projects' table:
    Columns: id, user_id, posted_at, title, description, url
    """

    def __init__(self, db: Optional[WorkanaBotDatabase] = None, default_user_id: Optional[int] = None):
        self._db = db if db is not None else WorkanaBotDatabase()
        # Respect explicit param, env var or fallback constant
        self._default_user_id = default_user_id or int(
            os.getenv("PROJECTS_DEFAULT_USER_ID", DEFAULT_USER_ID)
        )

        self.ensure_schema()
        self.ensure_project_skills_schema()
        self.ensure_default_user()

    # ---------------------------------
    # Schema (idempotent, English shape)
    # ---------------------------------
    def ensure_schema(self) -> None:
        """
        Creates the projects table if it does not exist.
        Does NOT add extra columns or constraints.
        """
        sql = """
        CREATE TABLE IF NOT EXISTS projects (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            user_id     INT NOT NULL,
            posted_at   DATETIME NULL,
            title       VARCHAR(255) NULL,
            description TEXT NULL,
            url         VARCHAR(255) NULL,
            CONSTRAINT fk_projects_user FOREIGN KEY (user_id)
                REFERENCES bot_users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        self._db.execute_non_query(sql)

    def ensure_project_skills_schema(self) -> None:
        """
        Creates project_skills table for storing scraped skills per project.
        Safe to run multiple times.
        """
        sql = """
        CREATE TABLE IF NOT EXISTS project_skills (
            id INT AUTO_INCREMENT PRIMARY KEY,
            project_id INT NOT NULL,
            skill_name VARCHAR(255) NOT NULL,
            skill_slug VARCHAR(255) NULL,
            skill_href VARCHAR(255) NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uniq_project_skill (project_id, skill_name, skill_slug),
            CONSTRAINT fk_project_skills_project FOREIGN KEY (project_id)
                REFERENCES projects(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        self._db.execute_non_query(sql)

    def ensure_default_user(self) -> None:
        """
        Guarantee a user exists to satisfy FK constraint on projects.user_id.
        """
        existing = self._db.execute_query(
            "SELECT id FROM bot_users WHERE id = %s OR telegram_user_id = %s LIMIT 1",
            (self._default_user_id, self._default_user_id),
        )
        if existing:
            return

        self._db.execute_non_query(
            "INSERT INTO bot_users (id, telegram_user_id, username, active) VALUES (%s, %s, %s, TRUE)",
            (self._default_user_id, self._default_user_id, "default_user"),
        )

    # ---------------------------------
    # Helpers
    # ---------------------------------
    @staticmethod
    def _to_dict_row(row: Tuple) -> Dict[str, Any]:
        return {
            "id": row[0],
            "user_id": row[1],
            "posted_at": row[2],
            "title": row[3],
            "description": row[4],
            "url": row[5],
        }

    # ---------------------------------
    # Queries
    # ---------------------------------
    def proyecto_exists_by_url(self, url: str) -> bool:
        sql = "SELECT 1 FROM projects WHERE url = %s LIMIT 1"
        return self._db.execute_scalar(sql, (url,)) is not None

    def insertar_proyecto(
        self,
        title: str,
        url: str,
        posted_at: Optional[datetime] = None,
        description: Optional[str] = None,
    ) -> Optional[int]:
        if posted_at is None:
            posted_at = datetime.now()  # Hora actual
        sql = (
            "INSERT INTO projects (user_id, posted_at, title, description, url) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        ok = self._db.execute_non_query(
            sql, (self._default_user_id, posted_at, title, description, url)
        )
        if not ok:
            return None
        return self._db.execute_scalar("SELECT id FROM projects WHERE url = %s ORDER BY id DESC LIMIT 1", (url,))

    def upsert_by_url(
        self,
        title: str,
        url: str,
        description: Optional[str] = None,
        posted_at: Optional[datetime] = None,
    ) -> Optional[int]:
        """
        Upsert without UNIQUE constraint:
        - If a row with same url exists -> UPDATE the most recent one.
        - Else -> INSERT.
        Returns affected row id or None.
        """
        existing = self._db.execute_query(
            "SELECT id FROM projects WHERE url = %s ORDER BY id DESC LIMIT 1", (url,)
        )
        if existing:
            pid = existing[0][0]
            ok = self.update_by_id(
                proyecto_id=pid,
                title=title,
                url=url,
                description=description,
                posted_at=posted_at,
            )
            return pid if ok else None
        return self.insertar_proyecto(title=title, url=url, description=description, posted_at=posted_at)

    def update_by_id(
        self,
    proyecto_id: int,
        title: Optional[str] = None,
        url: Optional[str] = None,
        description: Optional[str] = None,
        posted_at: Optional[datetime] = None,
    ) -> bool:
        """
        Updates provided fields only.
        """
        sets = []
        params: List[Any] = []
        if posted_at is not None:
            sets.append("posted_at = %s"); params.append(posted_at)
        if title is not None:
            sets.append("title = %s"); params.append(title)
        if description is not None:
            sets.append("description = %s"); params.append(description)
        if url is not None:
            sets.append("url = %s"); params.append(url)

        if not sets:
            return True  # nothing to update, consider success

        sql = f"UPDATE projects SET {', '.join(sets)} WHERE id = %s"
        params.append(proyecto_id)
        return self._db.execute_non_query(sql, tuple(params))

    def delete_by_id(self, proyecto_id: int) -> bool:
        """
        Hard delete (removes the row).
        """
        return self._db.execute_non_query("DELETE FROM projects WHERE id = %s", (proyecto_id,))

    def get_recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        sql = """
        SELECT id, user_id, posted_at, title, description, url
        FROM projects
        ORDER BY (posted_at IS NULL), posted_at DESC, id DESC
        LIMIT %s
        """
        rows = self._db.execute_query(sql, (limit,))
        return [self._to_dict_row(r) for r in rows]

    def get_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        sql = """
        SELECT id, user_id, posted_at, title, description, url
        FROM projects
        WHERE url = %s
        ORDER BY id DESC
        LIMIT 1
        """
        rows = self._db.execute_query(sql, (url,))
        return self._to_dict_row(rows[0]) if rows else None

    def search_by_skills(self, skills: List[str], limit: int = 100) -> List[Dict[str, Any]]:
        """
        Find projects whose title or description mention any of the provided skills.
        Uses a simple LIKE-based match against both the slug (with hyphens) and a
        space-separated variant (hyphens -> spaces) for broader coverage.
        """
        normalized = [s.strip().lower() for s in skills if isinstance(s, str) and s.strip()]
        if not normalized:
            return []

        clauses: List[str] = []
        params: List[Any] = []
        for skill in normalized:
            variants = {skill, skill.replace("-", " ")}
            for variant in variants:
                clauses.append("LOWER(CONCAT_WS(' ', title, description)) LIKE %s")
                params.append(f"%{variant}%")

        sql = f"""
        SELECT id, user_id, posted_at, title, description, url
        FROM projects
        WHERE {' OR '.join(clauses)}
        ORDER BY (posted_at IS NULL), posted_at DESC, id DESC
        LIMIT %s
        """
        params.append(limit)
        rows = self._db.execute_query(sql, tuple(params))
        return [self._to_dict_row(r) for r in rows]

    def get_projects_with_skills_since(
        self, since: Optional[datetime] = None, limit: int = 200
    ) -> List[Dict[str, Any]]:
        """
        Retrieve projects (ordered by posted_at DESC) with their stored skills.
        Only projects whose posted_at is on/after "since" are included when provided.
        """
        params: List[Any] = []
        where_clause = ""
        if since is not None:
            where_clause = "WHERE p.posted_at >= %s"
            params.append(since)

        sql_projects = f"""
        SELECT p.id, p.user_id, p.posted_at, p.title, p.description, p.url
        FROM projects p
        {where_clause}
        ORDER BY (p.posted_at IS NULL), p.posted_at DESC, p.id DESC
        LIMIT %s
        """
        params.append(limit)

        project_rows = self._db.execute_query(sql_projects, tuple(params))
        if not project_rows:
            return []

        project_ids = [row[0] for row in project_rows]
        skills_map: Dict[int, List[Dict[str, Any]]] = {pid: [] for pid in project_ids}

        placeholders = ",".join(["%s"] * len(project_ids))
        sql_skills = f"""
        SELECT project_id, skill_name, skill_slug, skill_href
        FROM project_skills
        WHERE project_id IN ({placeholders})
        """
        skill_rows = self._db.execute_query(sql_skills, tuple(project_ids))
        for pid, name, slug, href in skill_rows:
            if name:
                skills_map.setdefault(pid, []).append(
                    {"name": name, "slug": slug, "href": href}
                )

        projects: List[Dict[str, Any]] = []
        for row in project_rows:
            pid, user_id, posted_at, title, description, url = row
            projects.append(
                {
                    "id": pid,
                    "user_id": user_id,
                    "posted_at": posted_at,
                    "title": title,
                    "description": description,
                    "url": url,
                    "skills": skills_map.get(pid, []),
                }
            )

        return projects

    def bulk_insert(self, items: List[Dict[str, Any]]) -> int:
        count = 0
        for it in items:
            title = it.get("title") or it.get("titulo")
            url = it.get("url") or it.get("enlace")
            if not title or not url:
                continue
            if self.insertar_proyecto(
                title=title,
                url=url,
                description=it.get("description") or it.get("descripcion"),
                posted_at=it.get("posted_at") or it.get("fecha_hora"),
            ):
                count += 1
        return count

    # ---------------------------------
    # Skills
    # ---------------------------------
    def replace_project_skills(self, project_id: int, skills: List[Dict[str, Any]]) -> None:
        """
        Replace skills for a project with the provided list.
        Each skill may contain name, slug and href keys.
        """
        # Remove existing skills for the project first
        self._db.execute_non_query("DELETE FROM project_skills WHERE project_id = %s", (project_id,))

        for skill in skills:
            name = skill.get("name")
            if not name:
                continue
            slug = skill.get("slug")
            href = skill.get("href")
            self._db.execute_non_query(
                """
                INSERT INTO project_skills (project_id, skill_name, skill_slug, skill_href)
                VALUES (%s, %s, %s, %s)
                """,
                (project_id, name, slug, href),
            )


# Main de prueba (con inserción, lectura, actualización, listado y borrado físico)
if __name__ == "__main__":
    print("=== Testing proyectosDatabase (English schema) ===")
    try:
        db = proyectosDatabase()
        print("Instance created and schema ensured.")

        # 1) Read test
        recent = db.get_recent(limit=1)
        print(f"Connection test: {len(recent)} record(s) fetched.")

        # 2) Upsert test (insert or update last by url)
        test_url = "https://www.workana.com/job/test-project-original"
        pid = db.upsert_by_url(
            title="Proyecto de prueba (original)",
            url=test_url,
            description="Insertado por main() para prueba.",
            posted_at=datetime.now(),
        )
        print(f"Upsert ID: {pid}")

        # 3) Update test
        if pid:
            ok = db.update_by_id(pid, title="Proyecto de prueba (original) - actualizado")
            print(f"Update by id: {'OK' if ok else 'FAIL'}")

        # 4) Show recent
        print("\nRecent projects:")
        for p in db.get_recent(limit=5):
            print(f" - [{p['id']}] {p['title']} | {p['url']} | posted_at={p['posted_at']}")

        # 5) Hard delete test
        if pid:
            deleted = db.delete_by_id(pid)
            print(f"Delete test id {pid}: {'OK' if deleted else 'FAIL'}")

    except Exception as e:
        print(f"Error durante la prueba: {e}")
