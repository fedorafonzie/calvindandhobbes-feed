import requests
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

print("Script gestart: Ophalen van Calvin and Hobbes strip via de GoComics JSON API.")

# --- Stap 1: Haal de stripinformatie op via de verborgen API ---

# Dit is de URL naar de JSON-data voor de strip van vandaag.
API_URL = "https://www.gocomics.com/calvinandhobbes.json"
image_url = None

try:
    print(f"API aanroepen: {API_URL}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    response = requests.get(API_URL, headers=headers)
    response.raise_for_status()  # Stopt als er een HTTP-fout is
    
    # Converteer de response naar JSON-formaat
    data = response.json()
    
    # Haal de URL van de stripafbeelding uit de data.
    # Het pad is: ['data']['comics'][0]['image_urls']['large_image_url']
    image_url = data['data']['comics'][0]['image_urls']['large_image_url']

    if not image_url:
        print("FOUT: Kon de afbeeldings-URL niet vinden in de API-response.")
        print("Volledige response:", response.text)
        exit(1)

    print(f"SUCCES: Afbeelding URL gevonden: {image_url}")

except requests.exceptions.RequestException as e:
    print(f"FOUT: Kon de GoComics API niet bereiken. Fout: {e}")
    exit(1)
except (KeyError, IndexError) as e:
    print(f"FOUT: De structuur van de API-data is onverwacht. Fout: {e}")
    exit(1)


# --- Stap 2: Bouw de RSS-feed ---

COMIC_PAGE_URL = "https://www.gocomics.com/calvinandhobbes"

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