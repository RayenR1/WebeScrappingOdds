from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from lxml import html


liges = ['france/ligue-1', 'europe/champions-league', 'europe/europa-league', 'england/premier-league', 'spain/laliga', 'germany/bundesliga', 'italy/serie-a']

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
            while True:
                url = f"{base_url}/{league}-{season}/results/#/page/{page}/" if year != 2024 else f"{base_url}/{league}/results/#/page/{page}/"
                print(url)
                driver.get(url)  
                driver.delete_all_cookies()  
                driver.refresh() 
 
                time.sleep(10) 

                
                page_source = driver.page_source
                
               
                tree = html.fromstring(page_source)

               
                try:
                    WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "eventRow")]')))
                except:
                    print(f"Erreur : aucune donnée trouvée sur {league} {season}, page {page}. Passer à la saison suivante.")
                    break  # Passer à la saison suivante si une erreur se produit

                
                event_rows = tree.xpath('//div[contains(@class, "eventRow")]')

                if not event_rows:
                    print(f"Aucun element trouve pour {league} {season} page {page}")
                    

              
                for event_row in event_rows:
                    #print(event_row.text_content())  
                    match_time = event_row.xpath('.//p[@data-v-931a4162]/text()')
                    
                    teams = event_row.xpath('.//p[@class="participant-name truncate"]/text()')
                    home_score_xpath = './/a[@title and contains(@class, "cursor-pointer")]//div[contains(@class, "font-bold")][2]/text()'
                    away_score_xpath = './/a[@title and contains(@class, "cursor-pointer")]//div[contains(@class, "font-bold")][1]/text()'


                    odds_xpath = './/p[@data-v-18e31eaa and contains(@class, "height-content")]/text()'
                    odds = event_row.xpath(odds_xpath)                    
                    

                    if  len(teams) >= 2 :
                        away_scores = event_row.xpath(away_score_xpath)
                        if(len(away_scores)==2):
                            home_score = away_scores[0]
                            away_score = away_scores[1] 
                        else:
                            home_scores = event_row.xpath(home_score_xpath)
                            home_score=home_scores[0]
                            away_scoress = event_row.xpath(away_score_xpath)
                            away_score=away_scoress[0]
                            

                        home_team = teams[0]  
                        away_team = teams[1] 
                        odd_1 = odds[0].strip()  
                        odd_x = odds[1].strip()  
                        odd_2 = odds[2].strip()
                        print(f"Match time :{match_time[0]}")
                        print(f"{home_team} {home_score} - {away_score} {away_team}")
                        print(f"Cotes: 1: {odd_1}, X: {odd_x}, 2: {odd_2}")
                        print("-------------------------------------------------")
                    else:
                        print("Équipes, scores ou cotes non disponibles pour ce match.")
                page += 1 

                 

    driver.quit()


base_url = "https://www.oddsportal.com/football"
scrape_results(base_url, 2018, 2019)
