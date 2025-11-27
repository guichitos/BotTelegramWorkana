# user_skills_model.py
from workana_bot_database_model import WorkanaBotDatabase


DEFAULT_USER_ID = 123456789  # <-- tu valor por defecto


class UserSkills:
    def __init__(self, UserID: int | None = None, Database: WorkanaBotDatabase | None = None):
        if UserID is None:
            UserID = DEFAULT_USER_ID
        self.UserID = UserID
        self._db = Database if Database is not None else WorkanaBotDatabase()

    def normalize_skill(self, skill: str) -> str:
        """Normalize to Workana slug: lowercase, trim, spaces -> hyphens."""
        return "-".join(skill.strip().lower().split()) if skill else ""

    def _exists(self, skill_slug: str) -> bool:
        Query = "SELECT 1 FROM user_skills WHERE user_id = ? AND skill_slug = ? LIMIT 1"
        Result = self._db.execute_query(Query, (self.UserID, skill_slug))
        return bool(Result)

    def HasSkill(self, skill: str) -> bool:
        skill_slug = self.normalize_skill(skill)
        if not skill_slug:
            return False
        return self._exists(skill_slug)

    def GetAll(self) -> list[str]:
        """Returns all skills for the user (normalized)."""
        Query = "SELECT skill_slug FROM user_skills WHERE user_id = ?"
        Result = self._db.execute_query(Query, (self.UserID,))
        if not Result:
            return []
        return [self.normalize_skill(row[0]) for row in Result if row and row[0]]

    def Add(self, skill: str) -> bool:
        """Add a skill to the user (normalized)."""
        skill_slug = self.normalize_skill(skill)
        if not skill_slug:
            return False
        if self._exists(skill_slug):
            return True
        Query = "INSERT INTO user_skills (user_id, skill_slug) VALUES (?, ?)"
        return self._db.execute_non_query(Query, (self.UserID, skill_slug))

    def Remove(self, skill: str) -> bool:
        """Remove a specific skill from the user."""
        skill_slug = self.normalize_skill(skill)
        if not skill_slug:
            return False
        Query = "DELETE FROM user_skills WHERE user_id = ? AND skill_slug = ?"
        return self._db.execute_non_query(Query, (self.UserID, skill_slug))

    def ClearAll(self) -> bool:
        """Remove all skills for the user."""
        Query = "DELETE FROM user_skills WHERE user_id = ?"
        return self._db.execute_non_query(Query, (self.UserID,))

    @staticmethod
    def GetAllUsersSkills(Database: WorkanaBotDatabase) -> list[tuple[int, str]]:
        """Return all skills for all users (user_id, skill_slug)."""
        Query = "SELECT user_id, skill_slug FROM user_skills ORDER BY user_id"
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
