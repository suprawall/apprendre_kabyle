import requests
from bs4 import BeautifulSoup
import sqlite3
import random


base_dico_db = sqlite3.connect("dico.db")
base_dico_cursor = base_dico_db.cursor()

base_dico_cursor.execute("""
CREATE TABLE IF NOT EXISTS dico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mot_fr TEXT NOT NULL,
    mot_kabyle TEXT NOT NULL
)
""")
base_dico_db.commit()

dictionnaire_fr_kabyle = []

for lettre in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    
    url = f"https://apprendrelekabyle.com/dictionnaire-francais-kabyle-berbere/?dir=1&name_directory_startswith={lettre}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    
    mots_div = soup.find("div", class_="name_directory_names").find_all("div", class_="name_directory_name_box")
    l = len(dictionnaire_fr_kabyle)
    for content in mots_div:
        mot_fr = content.find("strong", role="term").get_text(strip=True)
        mot_kabyle = content.find("div", role="definition").get_text(strip=True)
        dictionnaire_fr_kabyle.append((mot_fr, mot_kabyle))
        
        base_dico_cursor.execute("INSERT INTO dico (mot_fr, mot_kabyle) VALUES (?, ?)", (mot_fr, mot_kabyle))
    base_dico_db.commit()
    
    """for mot_fr, mot_kabyle in dictionnaire_fr_kabyle:
        print(f"{mot_fr} : {mot_kabyle}")"""
        
    print(len(dictionnaire_fr_kabyle) - l, "mots trouvés pour la lettre", lettre)
    