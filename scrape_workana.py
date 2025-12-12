# scrape_workana.py
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from local_o_vps import entorno
from urllib.parse import parse_qs, urlparse
from models import Project, Skill

def CreateFirefoxDriver() -> webdriver.Firefox:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--ignore-certificate-errors")

    geckodriver_path = "C:/webdriver/geckodriver.exe" if entorno == "local" else "/usr/local/bin/geckodriver"
    service = Service(executable_path=geckodriver_path)
    return webdriver.Firefox(service=service, options=options)

def ScrapeWorkanaProjects(url: str) -> List[Project]:
    driver = CreateFirefoxDriver()
    wait = WebDriverWait(driver, 40)
    results: List[Project] = []

    try:
        driver.get(url)
        items = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".project-item.js-project")))

        for it in items:
            try:
                title = it.find_element(By.CSS_SELECTOR, ".project-title").text
                print(f"Scraping project: {title}")
                if not title:   # Skip if title is empty
                    continue
                desc = it.find_element(By.CSS_SELECTOR, ".html-desc.project-details").text
                link = it.find_element(By.CSS_SELECTOR, "a[href^='/job/']").get_attribute("href")
                if not link:
                    # Some cards may not include a valid URL; skip them to avoid None values
                    continue

                skill_nodes = it.find_elements(By.CSS_SELECTOR, "div.skills a.skill")
                skills: List[Skill] = []
                for node in skill_nodes:
                    try:
                        href = node.get_attribute("href") or ""
                        name = node.find_element(By.TAG_NAME, "h3").text.strip()
                        parsed = urlparse(href)
                        slug = parse_qs(parsed.query).get("skills", [""])[0]
                        skills.append(Skill(name=name, slug=slug, href=href))
                    except Exception:
                        continue

                results.append(Project(Title=title, Description=desc, Url=link, Skills=skills))
            except Exception:
                # omite item defectuoso y sigue
                continue
    finally:
        driver.quit()

    return results

if __name__ == "__main__":
    test_url = "https://www.workana.com/jobs?language=es&category=it-programming"
    try:
        projects = ScrapeWorkanaProjects(test_url)
        print(f"Se encontraron {len(projects)} proyectos.")
        for p in projects[:5]:
            print(f"- {p.Title} | {p.Url}")
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")