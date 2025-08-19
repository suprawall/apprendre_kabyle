import sqlite3
import random

def get_nombre_entrees():
    conn = sqlite3.connect("nouveau_testament.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM psaumes")
    total = cur.fetchone()[0]
    conn.close()
    return total

def afficher_entree(index):
    conn = sqlite3.connect("nouveau_testament.db")
    cur = conn.cursor()
    
    # L'index ici commence à 1 (pas 0)
    cur.execute("SELECT francais, kabyle FROM psaumes WHERE id = ?", (index,))
    row = cur.fetchone()
    conn.close()
    
    if row:
        francais, kabyle = row
        print(f"--- Entrée {index} ---")
        print("Français :", francais)
        print("Kabyle   :", kabyle)
    else:
        print("Aucune entrée trouvée pour cet index.")
import sqlite3

def afficher_toute_base():
    conn = sqlite3.connect("nouveau_testament.db")
    cur = conn.cursor()
    cur.execute("SELECT id, francais, kabyle FROM psaumes")
    rows = cur.fetchall()
    conn.close()

    print(f"Nombre total d'entrées : {len(rows)}\n")
    for id_, fr, kab in rows:
        print(f"--- Entrée {id_} ---")
        print(f"Français : {fr}")
        print(f"Kabyle   : {kab}")
        print()
        
print("Nombre d'entrées :", get_nombre_entrees())
# Exemple
afficher_entree(random.randint(1, get_nombre_entrees()))

afficher_toute_base()
