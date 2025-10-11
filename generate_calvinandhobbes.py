import requests
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import re

print("Script gestart: Ophalen van Calvin and Hobbes strip via HTML meta tag.")

# --- Stap 1: Haal de pagina op en extraheer de image URL uit de meta tag ---

COMIC_PAGE_URL = "https://www.gocomics.com/calvinandhobbes"
image_url = None

try:
    print(f"Pagina ophalen: {COMIC_PAGE_URL}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }
    response = requests.get(COMIC_PAGE_URL, headers=headers)
    response.raise_for_status()
    
    html_content = response.text
    
    # Zoek naar de 'og:image' meta tag met een regular expression
    # Dit is de meest betrouwbare manier om de URL te vinden.
    match = re.search(r'<meta property="og:image" content="([^"]+)"', html_content)
    
    if match:
        image_url = match.group(1)
        print(f"SUCCES: Afbeelding URL gevonden: {image_url}")
    else:
        print("FOUT: Kon de 'og:image' meta tag niet vinden in de HTML.")
        exit(1)

except requests.exceptions.RequestException as e:
    print(f"FOUT: Kon de GoComics pagina niet bereiken. Fout: {e}")
    exit(1)

# --- Stap 2: Bouw de RSS-feed ---

fg = FeedGenerator()
fg.id(COMIC_PAGE_URL)
fg.title('Calvin and Hobbes Strip')
fg.link(href=COMIC_PAGE_URL, rel='alternate')
fg.description('De dagelijkse Calvin and Hobbes strip.')
fg.language('en')

nu = datetime.now(timezone.utc)
datum_titel = nu.strftime("%Y-%m-%d")
comic_link = f"{COMIC_PAGE_URL}/{nu.strftime('%Y/%m/%d')}"

fe = fg.add_entry()
fe.id(image_url)
fe.title(f'Calvin and Hobbes - {datum_titel}')
fe.link(href=comic_link)
fe.pubDate(nu)
fe.description(f'<img src="{image_url}" alt="Calvin and Hobbes Strip voor {datum_titel}" />')

# --- Stap 3: Schrijf het XML-bestand weg ---

try:
    fg.rss_file('calvinandhobbes.xml', pretty=True)
    print("SUCCES: 'calvinandhobbes.xml' is aangemaakt met de strip van vandaag.")
except Exception as e:
    print(f"FOUT: Kon het bestand niet wegschrijven. Foutmelding: {e}")
    exit(1)