# user_skills_model.py
from workana_bot_database_model import WorkanaBotDatabase


DEFAULT_USER_ID = 123456789  # <-- tu valor por defecto


class UserSkills:
    def __init__(self, UserID: int | None = None, Database: WorkanaBotDatabase | None = None):
        if UserID is None:
            UserID = DEFAULT_USER_ID
        self.UserID = UserID
        self._db = Database if Database is not None else WorkanaBotDatabase()
        self._user_db_id: int | None = None
        self._is_registered = False
        self._load_user_db_id()

    def _load_user_db_id(self) -> None:
        """Cache the usuarios_bot.id linked to the telegram user (if any)."""
        result = self._db.execute_query(
            "SELECT id FROM usuarios_bot WHERE telegram_user_id = ? LIMIT 1",
            (self.UserID,),
        )
        if result:
            self._user_db_id = int(result[0][0])
            self._is_registered = True

    @property
    def is_registered(self) -> bool:
        return self._is_registered

    def _require_user_id(self) -> int | None:
        """Return DB user id or None if telegram user is not registered."""
        return self._user_db_id

    def normalize_skill(self, skill: str) -> str:
        """Normalize to Workana slug: lowercase, trim, spaces -> hyphens."""
        return "-".join(skill.strip().lower().split()) if skill else ""

    def _exists(self, skill_slug: str) -> bool:
        user_db_id = self._require_user_id()
        if user_db_id is None:
            return False
        Query = "SELECT 1 FROM user_skills WHERE user_id = ? AND skill_slug = ? LIMIT 1"
        Result = self._db.execute_query(Query, (user_db_id, skill_slug))
        return bool(Result)

    def HasSkill(self, skill: str) -> bool:
        skill_slug = self.normalize_skill(skill)
        if not skill_slug:
            return False
        return self._exists(skill_slug)

    def GetAll(self) -> list[str]:
        """Returns all skills for the user (normalized)."""
        user_db_id = self._require_user_id()
        if user_db_id is None:
            return []
        Query = "SELECT skill_slug FROM user_skills WHERE user_id = ?"
        Result = self._db.execute_query(Query, (user_db_id,))
        if not Result:
            return []
        return [self.normalize_skill(row[0]) for row in Result if row and row[0]]

    def Add(self, skill: str) -> bool:
        """Add a skill to the user (normalized)."""
        user_db_id = self._require_user_id()
        if user_db_id is None:
            return False
        skill_slug = self.normalize_skill(skill)
        if not skill_slug:
            return False
        if self._exists(skill_slug):
            return True
        Query = "INSERT INTO user_skills (user_id, skill_slug) VALUES (?, ?)"
        return self._db.execute_non_query(Query, (user_db_id, skill_slug))

    def Remove(self, skill: str) -> bool:
        """Remove a specific skill from the user."""
        user_db_id = self._require_user_id()
        if user_db_id is None:
            return False
        skill_slug = self.normalize_skill(skill)
        if not skill_slug:
            return False
        Query = "DELETE FROM user_skills WHERE user_id = ? AND skill_slug = ?"
        return self._db.execute_non_query(Query, (user_db_id, skill_slug))

    def ClearAll(self) -> bool:
        """Remove all skills for the user."""
        user_db_id = self._require_user_id()
        if user_db_id is None:
            return False
        Query = "DELETE FROM user_skills WHERE user_id = ?"
        return self._db.execute_non_query(Query, (user_db_id,))

    @staticmethod
    def GetAllUsersSkills(Database: WorkanaBotDatabase) -> list[tuple[int, str]]:
        """Return all skills for all users (telegram_user_id, skill_slug)."""
        Query = (
            "SELECT u.telegram_user_id, us.skill_slug "
            "FROM user_skills us "
            "JOIN usuarios_bot u ON us.user_id = u.id "
            "ORDER BY u.telegram_user_id"
        )
        return Database.execute_query(Query)


if __name__ == "__main__":

    user_id = 123456789

    skills_manager = UserSkills(user_id)

    print("=== Current skills ===")
    print(skills_manager.GetAll())

    print("\nAdding skills...")
    skills_manager.Add("Adobe Photoshop")
    skills_manager.Add("Microsoft Word")
    skills_manager.Add("Outlook")
    print(skills_manager.GetAll())

    print("\nRemoving skill 'data science'...")
    skills_manager.Remove("data science")
    print(skills_manager.GetAll())

    # Preguntar si limpiar todo
    answer = input("\n¿Deseas eliminar todas las skills agregadas durante esta prueba? (s/n): ").strip().lower()
    if answer == "s":
        skills_manager.ClearAll()
        print("Todas las skills fueron eliminadas.")
    else:
        print("Las skills se mantendrán.")

    print("\nEstado final:")
    print(skills_manager.GetAll())
