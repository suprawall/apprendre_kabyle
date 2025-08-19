import requests
from bs4 import BeautifulSoup
import sqlite3
import random

# Page principale
r = requests.get("https://www.amyag.com/")
soup = BeautifulSoup(r.text, "html.parser")

def clean():
    conn = sqlite3.connect("verbes.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM verbes")
    conn.commit()
    conn.close()
    print("✅ Table 'verbes' vidée avec succès.")
    
verb_conn = sqlite3.connect("verbes.db")
verb_cursor = verb_conn.cursor()

clean_verbes = True
if clean_verbes:
    clean()
    
# Création de la table verbes
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
verb_conn.commit()

# Récupération des liens verbes
verbes = []
print(len(soup.select("a[href^='/f/']")))
for a in soup.select("a[href^='/f/']"):
    href = a['href']  # e.g. "/f/OTIy/ili"
    parts = href.split('/')
    if len(parts) >= 3:
        id_, infinitif = parts[2], parts[3]
        verbes.append((infinitif, id_))

# Exemple : "ili", "OTIy"
print(f"J’ai trouvé {len(verbes)} verbes : {verbes[:5]}")

colonnes = [
    "verbe", "trad",
    "aorimp_2 si.", "aorimp_2 pl. m.", "aorimp_2 pl. f.",
    "aorfut_1 si.", "aorfut_2 si.", "aorfut_3 si. m.", "aorfut_3 si. f.",
    "aorfut_1 pl.", "aorfut_2 pl. m.", "aorfut_2 pl. f.", "aorfut_3 pl. m.", "aorfut_3 pl. f.",
    "pre_1 si.", "pre_2 si.", "pre_3 si. m.", "pre_3 si. f.",
    "pre_1 pl.", "pre_2 pl. m.", "pre_2 pl. f.", "pre_3 pl. m.", "pre_3 pl. f.",
    "pren_1 si.", "pren_2 si.", "pren_3 si. m.", "pren_3 si. f.",
    "pren_1 pl.", "pren_2 pl. m.", "pren_2 pl. f.", "pren_3 pl. m.", "pren_3 pl. f.",
    "para_", "parpp_", "parpn_"
]

# Ensuite, pour chacun :
for l, (infinitif, id_) in enumerate(verbes):
    
    url = f"https://www.amyag.com/f/{id_}/{infinitif}"
    vr = requests.get(url)
    vsoup = BeautifulSoup(vr.text, "html.parser")
    content_div = vsoup.find("div", id="content")

    verbe_kabyle = content_div.select_one("h3").text.strip()
    verbe_fr = content_div.find("div", class_="senses").get_text(strip=True)
    
    personnes = ["1 si.", "2 si.", "3 si. m", "3 si. f", "1 pl.", "2 pl. m", "2 pl. f", "3 pl. m", "3 pl. f"]
    temps = ["Aoriste (impératif)", "Aoriste (futur)", "Prétérit", "Prétérit négatif"]
    conjugaison = {"verbe": verbe_kabyle, "trad": verbe_fr}
    
    aorimp = content_div.find("ul", attrs={"data-aspect": "aorimp"})
    aorfut = content_div.find("ul", attrs={"data-aspect": "aorfut"})
    pre = content_div.find("ul", attrs={"data-aspect": "pre"})
    pren = content_div.find("ul", attrs={"data-aspect": "pren"})
    para = content_div.find("ul", attrs={"data-aspect": "para"})
    parpp = content_div.find("ul", attrs={"data-aspect": "parpp"})
    parpn = content_div.find("ul", attrs={"data-aspect": "parpn"})

    for i, temps_list in enumerate([aorimp, aorfut, pre, pren, para, parpp, parpn]):
        try:
            temps = temps_list.get("data-aspect")
        except AttributeError:
            print(f"Erreur de récupération pour le verbe {verbe_kabyle} ({verbe_fr}) à l'étape {i}.")
            continue
        list_conj = temps_list.find_all("span")
        list_conj_title = temps_list.find_all("span", attrs={"title": True})

        for j, span in enumerate(list_conj_title):
            i_span = list_conj.index(span)
            conjugaison[temps+"_"+list_conj[i_span - 1].text.strip()] = span.text.strip()
            list_conj.remove(span)
    
    data = []
    for keys in colonnes:
        if keys in conjugaison:
            data.append(conjugaison[keys])
        else:
            data.append(None)

    verb_cursor.execute("""
            INSERT INTO verbes VALUES (
                NULL, ?, ?,
                ?,?,?,
                ?,?,?,?,?,?,?,?,?,
                ?,?,?,?,?,?,?,?,?,
                ?,?,?,?,?,?,?,?,?,
                ?,?,?
            )
        """, data)
    verb_conn.commit()
    print(f"ligne: {l}  || Ajouté : {verbe_kabyle} ({verbe_fr}), exemple: {data[random.randint(0, len(data)-1)]})")
