import requests
from bs4 import BeautifulSoup
import sqlite3

# Connexion à la base SQLite
conn = sqlite3.connect("verbes.db")
verb_cursor = conn.cursor()

# Création de la table si elle n'existe pas
verb_cursor.execute("""
CREATE TABLE IF NOT EXISTS verbes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    infinitif TEXT NOT NULL,
    traduction TEXT,
    aoriste_imp_2si TEXT,
    aoriste_imp_2plm TEXT, aoriste_imp_2plf TEXT,
    aoriste_fut_1si TEXT, aoriste_fut_2si TEXT, aoriste_fut_3sim TEXT, aoriste_fut_3sif TEXT,
    aoriste_fut_1pl TEXT, aoriste_fut_2plm TEXT, aoriste_fut_2plf TEXT, aoriste_fut_3plm TEXT, aoriste_fut_3plf TEXT,
    preterit_1si TEXT, preterit_2si TEXT, preterit_3sim TEXT, preterit_3sif TEXT,
    preterit_1pl TEXT, preterit_2plm TEXT, preterit_2plf TEXT, preterit_3plm TEXT, preterit_3plf TEXT,
    pret_neg_1si TEXT, pret_neg_2si TEXT, pret_neg_3sim TEXT, pret_neg_3sif TEXT,
    pret_neg_1pl TEXT, pret_neg_2plm TEXT, pret_neg_2plf TEXT, pret_neg_3plm TEXT, pret_neg_3plf TEXT,
    part_aoriste TEXT, part_pret_pos TEXT, part_pret_neg TEXT
)
""")

# Récupération des liens depuis la page principale
r = requests.get("https://www.amyag.com/")
soup = BeautifulSoup(r.text, "html.parser")
verbes = []
for a in soup.select("a[href^='/f/']"):
    href = a['href']  # ex: "/f/OTIy/ili"
    parts = href.split('/')
    if len(parts) >= 4:
        id_, infinitif = parts[2], parts[3]
        verbes.append((infinitif, id_))

print(f"{len(verbes)} verbes trouvés.")

# Boucle sur chaque verbe
for infinitif, id_ in verbes:
    url = f"https://www.amyag.com/f/{id_}/{infinitif}"
    vr = requests.get(url)
    vsoup = BeautifulSoup(vr.text, "html.parser")
    content_div = vsoup.find("div", id="content")
    if not content_div:
        continue

    verbe_kabyle = content_div.select_one("h3").text.strip()
    verbe_fr = content_div.find("div", class_="senses").get_text(strip=True)

    conjugaison = {}
    # Liste des aspects dans la page
    aspects = {
        "aorimp": ["aoriste_imp_2si", "aoriste_imp_2plm", "aoriste_imp_2plf"],
        "aorfut": ["aoriste_fut_1si", "aoriste_fut_2si", "aoriste_fut_3sim", "aoriste_fut_3sif",
                   "aoriste_fut_1pl", "aoriste_fut_2plm", "aoriste_fut_2plf", "aoriste_fut_3plm", "aoriste_fut_3plf"],
        "pre": ["preterit_1si", "preterit_2si", "preterit_3sim", "preterit_3sif",
                "preterit_1pl", "preterit_2plm", "preterit_2plf", "preterit_3plm", "preterit_3plf"],
        "pren": ["pret_neg_1si", "pret_neg_2si", "pret_neg_3sim", "pret_neg_3sif",
                 "pret_neg_1pl", "pret_neg_2plm", "pret_neg_2plf", "pret_neg_3plm", "pret_neg_3plf"],
        "para": ["part_aoriste"],
        "parpp": ["part_pret_pos"],
        "parpn": ["part_pret_neg"]
    }

    # Extraction des conjugaisons
    for aspect, champs in aspects.items():
        ul_tag = content_div.find("ul", attrs={"data-aspect": aspect})
        if not ul_tag:
            for champ in champs:
                conjugaison[champ] = None
            continue

        if aspect in ["para", "parpp", "parpn"]:
            # participe, un seul élément
            conjugaison[champs[0]] = ul_tag.get_text(strip=True)
        else:
            spans = ul_tag.find_all("span", attrs={"title": True})
            for champ, span in zip(champs, spans):
                conjugaison[champ] = span.text.strip()

    # Insertion en base
    verb_cursor.execute("""
    INSERT INTO verbes (
        infinitif, traduction,
        aoriste_imp_2si, aoriste_imp_2plm, aoriste_imp_2plf,
        aoriste_fut_1si, aoriste_fut_2si, aoriste_fut_3sim, aoriste_fut_3sif,
        aoriste_fut_1pl, aoriste_fut_2plm, aoriste_fut_2plf, aoriste_fut_3plm, aoriste_fut_3plf,
        preterit_1si, preterit_2si, preterit_3sim, preterit_3sif,
        preterit_1pl, preterit_2plm, preterit_2plf, preterit_3plm, preterit_3plf,
        pret_neg_1si, pret_neg_2si, pret_neg_3sim, pret_neg_3sif,
        pret_neg_1pl, pret_neg_2plm, pret_neg_2plf, pret_neg_3plm, pret_neg_3plf,
        part_aoriste, part_pret_pos, part_pret_neg
    ) VALUES (
        :infinitif, :traduction,
        :aoriste_imp_2si, :aoriste_imp_2plm, :aoriste_imp_2plf,
        :aoriste_fut_1si, :aoriste_fut_2si, :aoriste_fut_3sim, :aoriste_fut_3sif,
        :aoriste_fut_1pl, :aoriste_fut_2plm, :aoriste_fut_2plf, :aoriste_fut_3plm, :aoriste_fut_3plf,
        :preterit_1si, :preterit_2si, :preterit_3sim, :preterit_3sif,
        :preterit_1pl, :preterit_2plm, :preterit_2plf, :preterit_3plm, :preterit_3plf,
        :pret_neg_1si, :pret_neg_2si, :pret_neg_3sim, :pret_neg_3sif,
        :pret_neg_1pl, :pret_neg_2plm, :pret_neg_2plf, :pret_neg_3plm, :pret_neg_3plf,
        :part_aoriste, :part_pret_pos, :part_pret_neg
    )
    """, {
        "infinitif": infinitif,
        "traduction": verbe_fr,
        **conjugaison
    })

# Commit et fermeture
conn.commit()
conn.close()

print("Insertion terminée.")
