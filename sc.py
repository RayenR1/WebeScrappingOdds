from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

# Initialise Selenium WebDriver
service = Service(executable_path=r'C:\Program Files\Google\Chrome\Application\chromedriver.exe')  # Mets à jour le chemin de ton chromedriver
driver = webdriver.Chrome(service=service)
driver.implicitly_wait(5)

liges = ['ligue-1', 'champions-league', 'europa-league', 'premier-league', 'laliga', 'bundesliga', 'serie-a']

def scrape_results(base_url, start_season, end_season):
    with open('results_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        header = ['League', 'Season', 'Match Result']  # Ajuste les colonnes selon tes besoins
        writer.writerow(header)
        
        for league in liges:
            for year in range(start_season, end_season + 1):
                season = f"{year}-{year + 1}"  # Générer le format YYYY-YYYY+1
                page = 1
                while True:
                    url = f"{base_url}/{league}/{season}/results/#/page/{page}/" if year != 2024 else f"{base_url}/{league}/results/#/page/{page}/"
                    driver.get(url)

                    try:
                        # Attendre que les résultats soient présents
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'result'))
                        )
                        
                        # Récupérer les résultats
                        results = driver.find_elements(By.CLASS_NAME, 'result')
                        if not results:
                            break  # Sort de la boucle si aucune donnée trouvée

                        for result in results:
                            writer.writerow([league, season, result.text])
                            print(f"{league} {season}: {result.text}")  # Affiche les résultats pour contrôle

                        page += 1  # Passe à la page suivante

                    except Exception as e:
                        print(f"Erreur pour {league} {season} page {page}: {e}")
                        break

base_url = "https://www.oddsportal.com/football"
scrape_results(base_url, 2018, 2024)

# Fermer le navigateur
driver.quit()
