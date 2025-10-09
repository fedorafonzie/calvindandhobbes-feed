import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

print("Script gestart: Ophalen van de dagelijks Calvin and Hobbes strip via Selenium.")

# --- Stap 1 & 2: Haal de pagina op met Selenium en vind de afbeeldings-URL ---

CALVINANDHOBBES_URL = 'https://www.gocomics.com/calvinandhobbes'
image_url = None

# Configureer Chrome om 'headless' te draaien (zonder zichtbaar browservenster)
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

driver = None
try:
    # Installeer en start de Chrome driver automatisch
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # NIEUW: Stel een timeout in voor het laden van de pagina zelf
    driver.set_page_load_timeout(30)
    
    print("Browser gestart. Bezig met laden van de pagina...")
    driver.get(CALVINANDHOBBES_URL)
    print("Pagina geladen. Wachten op het verschijnen van de afbeelding...")

    try:
        # AANGEPAST: Wacht maximaal 20 seconden op de afbeelding in een apart try/except blok
        wait = WebDriverWait(driver, 20)
        image_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'picture.item-asset-image img'))
        )
        image_url = image_element.get_attribute('src')
        print(f"SUCCES: Afbeelding URL gevonden: {image_url}")

    except TimeoutException:
        # NIEUW: Als de afbeelding niet wordt gevonden, maak een screenshot en print de HTML
        print("FOUT: Timeout bereikt. De afbeelding is niet gevonden binnen de tijdslimiet.")
        print("Bezig met maken van een debug screenshot (debug_screenshot.png)...")
        driver.save_screenshot('debug_screenshot.png')
        print("HTML van de huidige pagina:")
        print(driver.page_source)
        exit(1) # Stop het script met een foutcode

finally:
    # Sluit de browser altijd af, zelfs als er een fout optreedt
    if driver:
        driver.quit()
        print("Browser afgesloten.")

if not image_url:
    print("FOUT: Script eindigt omdat de image_url niet is gevonden.")
    exit(1)

# --- Stap 3: Bouw de RSS-feed ---

fg = FeedGenerator()
fg.id(CALVINANDHOBBES_URL)
fg.title('Calvin and Hobbes Strip')
fg.link(href=CALVINANDHOBBES_URL, rel='alternate')
fg.description('De dagelijkse Calvin and Hobbes strip.')
fg.language('en')

current_date = datetime.now(timezone.utc)
current_date_str = current_date.strftime("%Y-%m-%d")

fe = fg.add_entry()
fe.id(image_url)
fe.title(f'Calvin and Hobbes - {current_date_str}')
fe.link(href=CALVINANDHOBBES_URL)
fe.pubDate(current_date)
fe.description(f'<img src="{image_url}" alt="Calvin and Hobbes Strip voor {current_date_str}" />')

# --- Stap 4: Schrijf het XML-bestand weg ---

try:
    fg.rss_file('calvinandhobbes.xml', pretty=True)
    print("SUCCES: 'calvinandhobbes.xml' is aangemaakt met de strip van vandaag.")
except Exception as e:
    print(f"FOUT: Kon het bestand niet wegschrijven. Foutmelding: {e}")
    exit(1)