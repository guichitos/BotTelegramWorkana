# monitor_workana/projects_db.py
"""
proyectosDatabase (schema original): id, user_id, fecha_hora, titulo, descripcion, enlace.

__init__ : Inicializa el manager usando WorkanaBotDatabase y garantiza la existencia de la tabla y un usuario por defecto.
ensure_schema : Crea la tabla 'proyectos' con el esquema original si no existe (sin columnas extra).
ensure_default_user : Crea un usuario en usuarios_bot para cumplir el FK de proyectos.user_id si no existe.
_to_dict_row : Convierte una fila (tuple) en un diccionario con claves id/user_id/fecha_hora/titulo/descripcion/enlace.
proyecto_exists_by_url : Verifica si existe al menos un registro con el mismo enlace.
insertar_proyecto : Inserta un proyecto (user_id, fecha_hora, titulo, descripcion, enlace) y devuelve su ID o None.
upsert_by_url : Si existe un registro con ese enlace, lo actualiza; si no, inserta; devuelve el ID afectado.
update_by_id : Actualiza solo los campos provistos del proyecto indicado por ID.
delete_by_id : Elimina físicamente el registro indicado por ID.
get_recent : Obtiene los registros más recientes ordenados por fecha_hora (NULL al final) e ID.
get_by_url : Devuelve el último registro que coincide con el enlace (o None si no hay).
bulk_insert : Inserta múltiples proyectos omitiendo los que no tengan titulo o enlace.
__main__ : Prueba rápida: conexión/lectura, upsert, actualización, listado y borrado del registro de prueba.
"""

import os
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from workana_bot_database_model import WorkanaBotDatabase
from user_skills_model import DEFAULT_USER_ID


class proyectosDatabase:
    """
    Minimal controller for the original 'proyectos' table:
    Columns: id, user_id, fecha_hora, titulo, descripcion, enlace
    """

    def __init__(self, db: Optional[WorkanaBotDatabase] = None, default_user_id: Optional[int] = None):
        self._db = db if db is not None else WorkanaBotDatabase()
        # Respect explicit param, env var or fallback constant
        self._default_user_id = default_user_id or int(
            os.getenv("PROJECTS_DEFAULT_USER_ID", DEFAULT_USER_ID)
        )

        self.ensure_schema()
        self.ensure_default_user()

    # ---------------------------------
    # Schema (idempotent, original shape)
    # ---------------------------------
    def ensure_schema(self) -> None:
        """
        Creates the original table if it does not exist.
        Does NOT add extra columns or constraints.
        """
        sql = """
        CREATE TABLE IF NOT EXISTS proyectos (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            user_id     INT NOT NULL,
            fecha_hora  DATETIME NULL,
            titulo      VARCHAR(255) NULL,
            descripcion TEXT NULL,
            enlace      VARCHAR(255) NULL,
            CONSTRAINT fk_proyectos_usuario FOREIGN KEY (user_id)
                REFERENCES usuarios_bot(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        self._db.execute_non_query(sql)

    def ensure_default_user(self) -> None:
        """
        Guarantee a user exists to satisfy FK constraint on proyectos.user_id.
        """
        existing = self._db.execute_query(
            "SELECT id FROM usuarios_bot WHERE id = %s OR telegram_user_id = %s LIMIT 1",
            (self._default_user_id, self._default_user_id),
        )
        if existing:
            return

        self._db.execute_non_query(
            "INSERT INTO usuarios_bot (id, telegram_user_id, nombre_usuario, activo) VALUES (%s, %s, %s, TRUE)",
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
            "fecha_hora": row[2],
            "titulo": row[3],
            "descripcion": row[4],
            "enlace": row[5],
        }

    # ---------------------------------
    # Queries
    # ---------------------------------
    def proyecto_exists_by_url(self, url: str) -> bool:
        sql = "SELECT 1 FROM proyectos WHERE enlace = %s LIMIT 1"
        return self._db.execute_scalar(sql, (url,)) is not None

    def insertar_proyecto(
        self,
        titulo: str,
        enlace: str,
        fecha_hora: Optional[datetime] = None,
        descripcion: Optional[str] = None,
    ) -> Optional[int]:
        if fecha_hora is None:
            fecha_hora = datetime.now()  # Hora actual
        sql = (
            "INSERT INTO proyectos (user_id, fecha_hora, titulo, descripcion, enlace) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        ok = self._db.execute_non_query(
            sql, (self._default_user_id, fecha_hora, titulo, descripcion, enlace)
        )
        if not ok:
            return None
        return self._db.execute_scalar("SELECT id FROM proyectos WHERE enlace = %s ORDER BY id DESC LIMIT 1", (enlace,))

    def upsert_by_url(
        self,
        titulo: str,
        enlace: str,
        descripcion: Optional[str] = None,
        fecha_hora: Optional[datetime] = None,
    ) -> Optional[int]:
        """
        Upsert without UNIQUE constraint:
        - If a row with same enlace exists -> UPDATE the most recent one.
        - Else -> INSERT.
        Returns affected row id or None.
        """
        existing = self._db.execute_query(
            "SELECT id FROM proyectos WHERE enlace = %s ORDER BY id DESC LIMIT 1", (enlace,)
        )
        if existing:
            pid = existing[0][0]
            ok = self.update_by_id(
                proyecto_id=pid,
                titulo=titulo,
                enlace=enlace,
                descripcion=descripcion,
                fecha_hora=fecha_hora,
            )
            return pid if ok else None
        return self.insertar_proyecto(titulo=titulo, enlace=enlace, descripcion=descripcion, fecha_hora=fecha_hora)

    def update_by_id(
        self,
    proyecto_id: int,
        titulo: Optional[str] = None,
        enlace: Optional[str] = None,
        descripcion: Optional[str] = None,
        fecha_hora: Optional[datetime] = None,
    ) -> bool:
        """
        Updates provided fields only.
        """
        sets = []
        params: List[Any] = []
        if fecha_hora is not None:
            sets.append("fecha_hora = %s"); params.append(fecha_hora)
        if titulo is not None:
            sets.append("titulo = %s"); params.append(titulo)
        if descripcion is not None:
            sets.append("descripcion = %s"); params.append(descripcion)
        if enlace is not None:
            sets.append("enlace = %s"); params.append(enlace)

        if not sets:
            return True  # nothing to update, consider success

        sql = f"UPDATE proyectos SET {', '.join(sets)} WHERE id = %s"
        params.append(proyecto_id)
        return self._db.execute_non_query(sql, tuple(params))

    def delete_by_id(self, proyecto_id: int) -> bool:
        """
        Hard delete (removes the row).
        """
        return self._db.execute_non_query("DELETE FROM proyectos WHERE id = %s", (proyecto_id,))

    def get_recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        sql = """
        SELECT id, user_id, fecha_hora, titulo, descripcion, enlace
        FROM proyectos
        ORDER BY (fecha_hora IS NULL), fecha_hora DESC, id DESC
        LIMIT %s
        """
        rows = self._db.execute_query(sql, (limit,))
        return [self._to_dict_row(r) for r in rows]

    def get_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        sql = """
        SELECT id, user_id, fecha_hora, titulo, descripcion, enlace
        FROM proyectos
        WHERE enlace = %s
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
                clauses.append("LOWER(CONCAT_WS(' ', titulo, descripcion)) LIKE %s")
                params.append(f"%{variant}%")

        sql = f"""
        SELECT id, user_id, fecha_hora, titulo, descripcion, enlace
        FROM proyectos
        WHERE {' OR '.join(clauses)}
        ORDER BY (fecha_hora IS NULL), fecha_hora DESC, id DESC
        LIMIT %s
        """
        params.append(limit)
        rows = self._db.execute_query(sql, tuple(params))
        return [self._to_dict_row(r) for r in rows]

    def bulk_insert(self, items: List[Dict[str, Any]]) -> int:
        count = 0
        for it in items:
            titulo = it.get("titulo") or it.get("title")
            enlace = it.get("enlace") or it.get("url")
            if not titulo or not enlace:
                continue
            if self.insertar_proyecto(
                titulo=titulo,
                enlace=enlace,
                descripcion=it.get("descripcion") or it.get("description"),
                fecha_hora=it.get("fecha_hora") or it.get("posted_at"),
            ):
                count += 1
        return count


# Main de prueba (con inserción, lectura, actualización, listado y borrado físico)
if __name__ == "__main__":
    print("=== Testing proyectosDatabase (original schema) ===")
    try:
        db = proyectosDatabase()
        print("Instance created and schema ensured.")

        # 1) Read test
        recent = db.get_recent(limit=1)
        print(f"Connection test: {len(recent)} record(s) fetched.")

        # 2) Upsert test (insert or update last by enlace)
        test_url = "https://www.workana.com/job/test-proyecto-original"
        pid = db.upsert_by_url(
            titulo="Proyecto de prueba (original)",
            enlace=test_url,
            descripcion="Insertado por main() para prueba.",
            fecha_hora=datetime.now(),
        )
        print(f"Upsert ID: {pid}")

        # 3) Update test
        if pid:
            ok = db.update_by_id(pid, titulo="Proyecto de prueba (original) - actualizado")
            print(f"Update by id: {'OK' if ok else 'FAIL'}")

        # 4) Show recent
        print("\nRecent proyectos:")
        for p in db.get_recent(limit=5):
            print(f" - [{p['id']}] {p['titulo']} | {p['enlace']} | fecha_hora={p['fecha_hora']}")

        # 5) Hard delete test
        if pid:
            deleted = db.delete_by_id(pid)
            print(f"Delete test id {pid}: {'OK' if deleted else 'FAIL'}")

    except Exception as e:
        print(f"Error durante la prueba: {e}")
