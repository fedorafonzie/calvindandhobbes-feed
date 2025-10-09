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

# URL van de Calvin and Hobbes comic pagina
CALVINANDHOBBES_URL = 'https://www.gocomics.com/calvinandhobbes'

# Stap 1: Haal de webpagina op
try:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(CALVINANDHOBBES_URL, headers=headers)
    response.raise_for_status()
    print("SUCCES: GoComics pagina HTML opgehaald.")
except requests.exceptions.RequestException as e:
    print(f"FOUT: Kon GoComics pagina niet ophalen. Fout: {e}")
    exit(1)

# Stap 2: Zoek met een regular expression naar de afbeeldings-URL
print("Zoeken naar de afbeeldings-URL met een regular expression...")

# --- CORRECTIE ---
# Dit patroon zoekt naar het <picture> element met de class 'item-asset-image'
# en pakt vervolgens de URL uit het <img> element dat daarin staat.
match = re.search(r'<picture class="item-asset-image">\s*<img src="([^"]+)"', response.text)

if not match:
    print("FOUT: Kon het URL-patroon niet vinden in de broncode van de pagina.")
    exit(1)

# match.group(1) bevat de URL die we zoeken.
image_url = match.group(1)
print(f"SUCCES: Afbeelding URL gevonden via Regular Expression: {image_url}")
# --- EINDE CORRECTIE ---
    
# Stap 3: Bouw de RSS-feed
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

try:
    fg.rss_file('calvinandhobbes.xml', pretty=True)
    print("SUCCES: 'calvinandhobbes.xml' is aangemaakt met de strip van vandaag.")
except Exception as e:
    print(f"FOUT: Kon het bestand niet wegschrijven. Foutmelding: {e}")
    exit(1)
