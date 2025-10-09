import time
from selenium import webdriver
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
    
    print(f"SUCCES: Browser gestart. Bezig met laden van: {CALVINANDHOBBES_URL}")
    driver.get(CALVINANDHOBBES_URL)

    # Wacht maximaal 15 seconden tot de stripafbeelding geladen is
    # Dit is de belangrijkste stap: we wachten tot de JavaScript klaar is.
    wait = WebDriverWait(driver, 15)
    image_element = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'picture.item-asset-image img'))
    )
    
    # Haal de URL op uit het 'src' attribuut van de afbeelding
    image_url = image_element.get_attribute('src')

    if not image_url:
        print("FOUT: Kon de afbeeldings-URL niet vinden na het laden van de pagina.")
        exit(1)
        
    print(f"SUCCES: Afbeelding URL gevonden: {image_url}")

finally:
    # Sluit de browser altijd af, zelfs als er een fout optreedt
    if driver:
        driver.quit()
        print("SUCCES: Browser afgesloten.")

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