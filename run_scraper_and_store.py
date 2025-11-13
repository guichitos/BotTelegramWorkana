# run_scrape_and_store.py
from scrape_workana import ScrapeWorkanaProjects
from projects_db_manager import ProjectRepository

def Run(url: str) -> int:
    projects = ScrapeWorkanaProjects(url)          # solo extrae
    repo = ProjectRepository()                     # solo guarda
    count = repo.SaveProjects(projects)            # persistencia
    return count

if __name__ == "__main__":
    test_url = "https://www.workana.com/jobs?language=en%2Ces&query=python"
    print("Iniciando scraping y almacenamiento de proyectos...")
    try:
        inserted_count = Run(test_url)
        print(f"✅ Inserted/Updated: {inserted_count}")
    except Exception as e:
        print(f"❌ Error ejecutando Run: {e}")

