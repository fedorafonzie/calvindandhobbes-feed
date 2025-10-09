import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

print("Script gestart: Ophalen van de strip via undetected-chromedriver.")

# --- Stap 1 & 2: Haal de pagina op en vind de afbeeldings-URL ---

CALVINANDHOBBES_URL = 'https://www.gocomics.com/calvinandhobbes'
image_url = None

# Configureer de browser-opties
options = uc.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = None
try:
    print("Browser (undetected-chromedriver) wordt gestart...")
    # AANGEPAST: We specificeren de Chrome-versie om de mismatch te voorkomen.
    driver = uc.Chrome(options=options, version_main=140)
    
    print(f"Pagina laden: {CALVINANDHOBBES_URL}")
    driver.get(CALVINANDHOBBES_URL)

    try:
        wait = WebDriverWait(driver, 30)
        image_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'picture.item-asset-image img'))
        )
        image_url = image_element.get_attribute('src')
        print(f"SUCCES: Afbeelding URL gevonden: {image_url}")

    except TimeoutException:
        print("FOUT: Timeout bereikt. De afbeelding is niet gevonden.")
        driver.save_screenshot('debug_screenshot.png')
        print("HTML van de huidige pagina:")
        print(driver.page_source)
        exit(1)

finally:
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