import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone, timedelta

print("Script gestart: Ophalen van klassieke C&H strip via de dag-pagina.")

# --- Stap 1: Bepaal welke klassieke strip we vandaag ophalen ---

# De strip liep van 18 november 1985 tot 31 december 1995.
start_datum_strip = datetime(1985, 11, 18)
eind_datum_strip = datetime(1995, 12, 31)
totaal_dagen_strip = (eind_datum_strip - start_datum_strip).days + 1

# We gebruiken een vast startpunt om de cyclus voorspelbaar te maken.
start_punt_cyclus = datetime(2020, 1, 1)
vandaag = datetime.now()
dagen_verstreken = (vandaag - start_punt_cyclus).days

# Bereken welke dag in de strip-cyclus het vandaag is.
cyclus_dag_index = dagen_verstreken % totaal_dagen_strip
huidige_strip_datum = start_datum_strip + timedelta(days=cyclus_dag_index)

# Formatteer de datum voor de URL van de GoComics pagina
jaar = huidige_strip_datum.strftime('%Y')
maand = huidige_strip_datum.strftime('%m')
dag = huidige_strip_datum.strftime('%d')

comic_page_url = f"https://www.gocomics.com/calvinandhobbes/{jaar}/{maand}/{dag}"
image_url = None

# --- Stap 2: Haal de pagina op en extraheer de image URL ---

try:
    print(f"Pagina ophalen: {comic_page_url}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
    response = requests.get(comic_page_url, headers=headers)
    response.raise_for_status()

    # Gebruik BeautifulSoup om de HTML te parsen
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Zoek naar de picture-tag met de class 'item-asset-image' en haal de src van de img-tag eruit
    picture_tag = soup.find('picture', class_='item-asset-image')
    if picture_tag:
        img_tag = picture_tag.find('img')
        if img_tag and img_tag.has_attr('src'):
            image_url = img_tag['src']
            print(f"SUCCES: Afbeelding URL gevonden: {image_url}")
        else:
             print("FOUT: Kon de <img> tag of de 'src' attributie niet vinden.")
             exit(1)
    else:
        print("FOUT: Kon de <picture> tag met class 'item-asset-image' niet vinden.")
        exit(1)

except requests.exceptions.RequestException as e:
    print(f"FOUT: Kon de GoComics pagina niet bereiken. Fout: {e}")
    exit(1)

# --- Stap 3: Bouw en schrijf de RSS-feed ---

fg = FeedGenerator()
fg.id(comic_page_url)
fg.title('Calvin and Hobbes Strip')
fg.link(href='https://www.gocomics.com/calvinandhobbes', rel='alternate')
fg.description('Een dagelijkse klassieke Calvin and Hobbes strip.')
fg.language('en')

datum_titel = huidige_strip_datum.strftime("%Y-%m-%d")

fe = fg.add_entry()
fe.id(image_url)
fe.title(f'Calvin and Hobbes - {datum_titel}')
fe.link(href=comic_page_url)
fe.pubDate(vandaag.replace(hour=8, minute=0, second=0, microsecond=0).astimezone(timezone.utc))
fe.description(f'<img src="{image_url}" alt="Calvin and Hobbes Strip voor {datum_titel}" />')

try:
    fg.rss_file('calvinandhobbes.xml', pretty=True)
    print("SUCCES: 'calvinandhobbes.xml' is aangemaakt met de strip van vandaag.")
except Exception as e:
    print(f"FOUT: Kon het bestand niet wegschrijven. Foutmelding: {e}")
    exit(1)