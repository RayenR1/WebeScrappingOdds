import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from lxml import html

liges = ['brazil/serie-a-betano']
data = []

def scrape_results(base_url, start_season, end_season):
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")
    
    driver_path = "C:/Users/jlassi/Desktop/datasetR1/chromedriver.exe"
    service = ChromeService(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    for league in liges:
        for year in range(start_season, end_season + 1):
            season = f"{year}-{year + 1}"
            page = 1
            match_date_avant = ""
            while True:
                url = f"{base_url}/{league}-{season}/results/#/page/{page}/" if year != 2024 else f"{base_url}/{league}/results/#/page/{page}/"
                print(url)
                driver.get(url)
                driver.delete_all_cookies()
                driver.refresh()
                time.sleep(4)
                page_source = driver.page_source
                tree = html.fromstring(page_source)
                
                try:
                    WebDriverWait(driver, 18).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "eventRow")]')))
                except:
                    print(f"Erreur : aucune donnée trouvée sur {league} {season}, page {page}. Passer à la saison suivante.")
                    break
                
                event_rows = tree.xpath('//div[contains(@class, "eventRow")]')
                if not event_rows:
                    print(f"Aucun element trouve pour {league} {season} page {page}")
                    break
                
                for event_row in event_rows:
                    match_time = event_row.xpath('.//p[@data-v-931a4162]/text()')
                    teams = event_row.xpath('.//p[@class="participant-name truncate"]/text()')
                    home_score_xpath = './/a[@title and contains(@class, "cursor-pointer")]//div[contains(@class, "font-bold")][2]/text()'
                    away_score_xpath = './/a[@title and contains(@class, "cursor-pointer")]//div[contains(@class, "font-bold")][1]/text()'
                    odds_xpath = './/p[@data-v-18e31eaa and contains(@class, "height-content")]/text()'
                    odds = event_row.xpath(odds_xpath)
                    match_date_xpath = './/div[contains(@class, "text-black-main font-main w-full truncate text-xs font-normal leading-5")]/text()'
                    match_datee = event_row.xpath(match_date_xpath)
                    all_odds_elements = event_row.xpath('.//p[contains(@class, "height-content")]')
                    
                    winning_odds = []
                    for element in all_odds_elements:
                        class_attr = element.attrib.get('class', '')
                        if 'gradient-green' in class_attr and 'hover' in class_attr:
                            if class_attr.index('gradient-green') < class_attr.index('hover'):
                                winning_odds.append(element.text_content().strip())
                    
                    if len(teams) >= 2:
                        away_scores = event_row.xpath(away_score_xpath)
                        if len(away_scores) == 2:
                            home_score = away_scores[0]
                            away_score = away_scores[1]
                        else:
                            home_scores = event_row.xpath(home_score_xpath)
                            home_score = home_scores[0] if home_scores else "N/A"
                            away_scoress = event_row.xpath(away_score_xpath)
                            away_score = away_scoress[0] if away_scores else "N/A"

                        if len(match_datee) == 0:
                            match_date = match_date_avant
                        else:
                            match_date = match_datee[0]
                            match_date_avant = match_datee[0]

                        championat = league
                        saison = season
                        home_team = teams[0]
                        away_team = teams[1]
                        odd_1 = odds[0].strip() if len(odds) >= 3 else "N/A"
                        odd_x = odds[1].strip() if len(odds) >= 3 else "N/A"
                        odd_2 = odds[2].strip() if len(odds) >= 3 else "N/A"
                        winning_odd = winning_odds[0] if winning_odds else "N/A"
                        
                        Gangnant = None
                        if winning_odds:
                            if winning_odd == odd_1:
                                Gangnant = 1  # Victoire domicile
                            elif winning_odd == odd_x:
                                Gangnant = 0  # Match nul
                            elif winning_odd == odd_2:
                                Gangnant = 2  # Victoire extérieure

                        data.append([saison, championat, match_date, match_time[0], home_team, home_score, away_score, away_team, odd_1, odd_x, odd_2, Gangnant])

                        print(f"Saison : {saison}")
                        print(f"Championat : {championat}")
                        print(f"match date : {match_date}")
                        print(f"Match time : {match_time[0]}")
                        print(f"{home_team} {home_score} - {away_score} {away_team}")
                        print(f"Cotes: 1: {odd_1}, X: {odd_x}, 2: {odd_2}")
                        print(f"Gangnant : {Gangnant}")
                        print("-------------------------------------------------")
                    else:
                        print("Équipes, scores ou cotes non disponibles pour ce match.")
                    
                page += 1
                
    driver.quit()

base_url = "https://www.oddsportal.com/football"
scrape_results(base_url, 2024, 2024)
df = pd.DataFrame(data, columns=["Saison", "Championat", "Date", "Heure", "Équipe Domicile", "Score Domicile", "Score Extérieur", "Équipe Extérieur", "Cote 1", "Cote X", "Cote 2", "Gangnant"])
print(df)
with open("C:/Users/jlassi/Desktop/datasetR1/matches.csv", "w", newline="") as f:
    df.to_csv(f, index=False)
    print("Les données ont été exportées avec succès dans matches.csv")
