from workana_bot_database_model import WorkanaBotDatabase

class User:
    def __init__(self, UserID: int, Database: WorkanaBotDatabase):
        self.UserID = UserID
        self.Username = None
        self._IsRegistered = False
        self._IsActivated = False
        self._db = Database
        self._LoadUserData()

    def _LoadUserData(self):
        Query = "SELECT username, active FROM bot_users WHERE telegram_user_id = ?"
        Result = self._db.execute_query(Query, (self.UserID,))
        if Result:
            self.Username = Result[0][0]
            self._IsRegistered = True
            self._IsActivated = bool(Result[0][1])

    @property
    def IsRegistered(self) -> bool:
        return self._IsRegistered

    @property
    def IsActivated(self) -> bool:
        return self._IsActivated

    def Register(self, Username: str) -> bool:
        if self.IsRegistered:
            if self.IsActivated:
                return False

            Query = (
                "UPDATE bot_users SET username = ?, active = TRUE "
                "WHERE telegram_user_id = ?"
            )
            Success = self._db.execute_non_query(Query, (Username, self.UserID))
            if Success:
                self.Username = Username
                self._IsActivated = True
            return Success

        Query = "INSERT INTO bot_users (telegram_user_id, username) VALUES (?, ?)"
        Success = self._db.execute_non_query(Query, (self.UserID, Username))
        if Success:
            self.Username = Username
            self._IsRegistered = True
            self._IsActivated = False
        return Success

    def Activate(self) -> bool:
        if not self.IsRegistered:
            return False
        Query = "UPDATE bot_users SET active = TRUE WHERE telegram_user_id = ?"
        Success = self._db.execute_non_query(Query, (self.UserID,))
        if Success:
            self._IsActivated = True
        return Success

    def Deactivate(self) -> bool:
        if not self.IsRegistered:
            return False
        Query = "UPDATE bot_users SET active = FALSE WHERE telegram_user_id = ?"
        Success = self._db.execute_non_query(Query, (self.UserID,))
        if Success:
            self._IsActivated = False
        return Success

    def SoftDelete(self) -> bool:
        """Marca al usuario como inactivo sin borrar el registro."""
        if not self.IsRegistered:
            return False

        Query = "UPDATE bot_users SET active = FALSE WHERE telegram_user_id = ?"
        Success = self._db.execute_non_query(Query, (self.UserID,))
        if Success:
            self._IsActivated = False
        return Success

    def Delete(self) -> bool:
        if not self.IsRegistered:
            return False
        Query = "DELETE FROM bot_users WHERE telegram_user_id = ?"
        Success = self._db.execute_non_query(Query, (self.UserID,))
        if Success:
            self._IsRegistered = False
            self._IsActivated = False
            self.Username = None
        return Success

    @staticmethod
    def GetAllActive(Database: WorkanaBotDatabase) -> list[tuple[int, str]]:
        Query = "SELECT telegram_user_id, username FROM bot_users WHERE active = TRUE"
        return Database.execute_query(Query)


if __name__ == "__main__":
    db = WorkanaBotDatabase()
    user_id = 123456789
    username = "usuario_prueba"

    print("=== Creando instancia de usuario ===")
    user = User(user_id, db)
    print(f"UserID: {user.UserID}")
    print(f"Username: {user.Username}")
    print(f"IsRegistered: {user.IsRegistered}")
    print(f"IsActivated: {user.IsActivated}")

    # Registrar si no existe
    if not user.IsRegistered:
        print("\nUsuario no existe. Registrando...")
        if user.Register(username):
            print("Usuario registrado correctamente.")
        else:
            print("Error al registrar el usuario.")

    # Leer nuevamente
    print("\n=== Leyendo datos tras registro ===")
    user = User(user_id, db)
    print(f"UserID: {user.UserID}")
    print(f"Username: {user.Username}")
    print(f"IsRegistered: {user.IsRegistered}")
    print(f"IsActivated: {user.IsActivated}")

    # Borrar usuario
    print("\nBorrando usuario...")
    if user.Delete():
        print("Usuario borrado correctamente.")
    else:
        print("No se pudo borrar el usuario.")

    # Leer nuevamente tras borrado
    print("\n=== Leyendo datos tras borrado ===")
    user = User(user_id, db)
    print(f"UserID: {user.UserID}")
    print(f"Username: {user.Username}")
    print(f"IsRegistered: {user.IsRegistered}")
    print(f"IsActivated: {user.IsActivated}")
