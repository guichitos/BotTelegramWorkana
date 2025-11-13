#user_skills.py
from workana_bot_database_model import WorkanaBotDatabase


DEFAULT_USER_ID = 123456789  # <-- tu valor por defecto

class UserSkills:
    def __init__(self, UserID: int | None = None, Database: WorkanaBotDatabase | None = None):
        if UserID is None:
            UserID = DEFAULT_USER_ID
        self.UserID = UserID
        self._db = Database if Database is not None else WorkanaBotDatabase()

    def _normalize_skill(self, skill: str) -> str:
        """Normalize to Workana slug: lowercase, trim, spaces -> hyphens."""
        return "-".join(skill.strip().lower().split())

    def GetAll(self) -> list[str]:
        """Returns all skills for the user (normalized)."""
        Query = "SELECT skill_slug FROM user_skills WHERE user_id = ?"
        Result = self._db.execute_query(Query, (self.UserID,))
        if not Result:
            return []
        return [self._normalize_skill(row[0]) for row in Result if row and row[0]]

    def Add(self, skill: str) -> bool:
        """Add a skill to the user (normalized)."""
        skill_slug = self._normalize_skill(skill)
        print(f"Intentando insertar skill: {skill_slug}")
        Query = "INSERT IGNORE INTO user_skills (user_id, skill_slug) VALUES (?, ?)"
        result = self._db.execute_non_query(Query, (self.UserID, skill_slug))
        print(f"Resultado execute_non_query: {result}")
        return result


    def Remove(self, skill: str) -> bool:
        """Remove a specific skill from the user."""
        skill_slug = self._normalize_skill(skill)
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

