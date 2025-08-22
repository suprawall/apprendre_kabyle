import re
import sqlite3
import fitz  # PyMuPDF

# --- Connexion à la base ---
conn = sqlite3.connect("nouveau_testament.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS psaumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    francais TEXT,
    kabyle TEXT
)
""")

# --- Extraction du texte ---
pdf_path = "nouveau testament francais kabyle.pdf"
doc = fitz.open(pdf_path)

# Variables pour stocker le texte
fr_paragraphs = []
kab_paragraphs = []

mapping_caract = {
    '[': 'ṛ',
    '\x90': 'ɛ',
    '%': 'ḥ',
    '\x07': 'ǧ',
    '$': 'Ḥ',   
}

# Expression régulière pour détecter le début d'un verset / paragraphe
num_pattern = re.compile(r"(?=\n?\d+\s)")

def nettoyer_bloc(texte):
    return " ".join(texte.split())  # supprime les \n internes

def clean_text(text):
    # Nettoyage des caractères spécifiques
    for old, new in mapping_caract.items():
        text = text.replace(old, new)
    return text

doc = fitz.open("nouveau testament francais kabyle.pdf")

# On suppose que chaque page a d'abord le français puis le kabyle (comme dans ton extrait)
for page in doc:
    text = page.get_text("blocks")  # blocs = positions
    
    # On trie par position Y pour garder l'ordre
    text.sort(key=lambda b: (b[1], b[0]))

    # On sépare les colonnes français/kabyle par position X
    # On détermine la coupure centrale
    mid_x = page.rect.width / 2

    fr_text = []
    kab_text = []
    for block in text:
        x0, y0, x1, y1, bloc_text, *_ = block
        if x1 < mid_x:  # colonne gauche = français
            fr_text.append(bloc_text.strip())
        else:  # colonne droite = kabyle
            kab_text.append(bloc_text.strip())

    # On fusionne les lignes
    fr_lines = "\n".join(fr_text)
    kab_lines = "\n".join(kab_text)

    # On garde uniquement les paragraphes commençant par un numéro
    fr_lines = [l.strip() for l in re.split(num_pattern, fr_lines) if l.strip()]
    kab_lines = [l.strip() for l in re.split(num_pattern, kab_lines) if l.strip()]

    kab_lines = [clean_text(l) for l in kab_lines]
    
    print(len(fr_lines), len(kab_lines))  # Pour déboguer, on affiche le nombre de lignes
    exit(0)  # Pour déboguer, on affiche le texte français
    
    fr_paragraphs.extend(fr_lines)
    kab_paragraphs.extend(kab_lines)

# --- Insertion en base ---
for fr, kab in zip(fr_paragraphs, kab_paragraphs):
    cur.execute("INSERT INTO psaumes (francais, kabyle) VALUES (?, ?)", (fr, kab))

conn.commit()
conn.close()

print(f"Import terminé : {len(fr_paragraphs)} entrées insérées.")