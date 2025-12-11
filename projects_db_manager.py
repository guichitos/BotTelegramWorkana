# projects_db_manager.py
from typing import List
from datetime import datetime
from projects_db import proyectosDatabase
from models import Project
from send_telegram_message import mensaje as send_telegram_message

class ProjectRepository:
    def __init__(self):
        self._db = proyectosDatabase()

    def SaveProjects(self, projects: List[Project]) -> int:
        inserted = 0
        for p in projects:
            was_existing = self._db.proyecto_exists_by_url(p.Url)

            ok_id = self._db.upsert_by_url(
                titulo=p.Title,
                enlace=p.Url,
                descripcion=p.Description,
                fecha_hora=datetime.now()
            )
            if ok_id:
                inserted += 1
                if p.Skills:
                    try:
                        self._db.replace_project_skills(ok_id, p.Skills)
                    except Exception as ex:
                        print(f"Error guardando skills para proyecto {ok_id}: {ex}")
                if not was_existing:
                    try:
                        send_telegram_message(p.Title, p.Url)
                    except Exception as ex:
                        print(f"Error enviando mensaje a Telegram: {ex}")
        return inserted
    
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