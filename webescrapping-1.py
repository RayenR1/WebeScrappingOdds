from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from lxml import html

# Liste des ligues
liges = ['france/ligue-1', 'europe/champions-league', 'europe/europa-league', 'england/premier-league', 'spain/laliga', 'germany/bundesliga', 'italy/serie-a']

def scrape_results(base_url, start_season, end_season):
    # Configuration du WebDriver (pour Chrome)
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")  # Lancer Chrome sans interface graphique
    
    driver_path = "C:/Users/jlassi/Desktop/datasetR1/chromedriver.exe"  # Chemin vers ChromeDriver
    service = ChromeService(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    for league in liges:
        for year in range(start_season, end_season + 1):
            season = f"{year}-{year + 1}"  # Générer le format YYYY-YYYY+1
            page = 1
            while True:
                url = f"{base_url}/{league}-{season}/results/#/page/{page}/" if year != 2024 else f"{base_url}/{league}/results/#/page/{page}/"
                print(url)
                driver.get(url)  # Charger la page avec Selenium
                driver.delete_all_cookies()  
                driver.refresh() 
 
                time.sleep(10)  # Attendre quelques secondes pour que le JavaScript s'exécute

                # Obtenir la source de la page
                page_source = driver.page_source
                
                # Utiliser lxml pour parser le HTML
                tree = html.fromstring(page_source)

                # Attendre que la div contenant "eventRow" soit présente
                try:
                    WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "eventRow")]')))
                except:
                    print(f"Erreur : aucune donnée trouvée sur {league} {season}, page {page}. Passer à la saison suivante.")
                    break  # Passer à la saison suivante si une erreur se produit

                # Chercher toutes les divs avec la classe "eventRow"
                event_rows = tree.xpath('//div[contains(@class, "eventRow")]')

                if not event_rows:
                    print(f"Aucun élément trouvé pour {league} {season} page {page}")
                    #break  # Sortir de la boucle si aucune donnée trouvée

                # Afficher les résultats extraits
                for event_row in event_rows:
                    print(event_row.text_content())  # Affiche le texte contenu dans la div

                page += 1 

                 

    driver.quit()

# URL de base
base_url = "https://www.oddsportal.com/football"
scrape_results(base_url, 2018, 2024)
