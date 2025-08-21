import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import random
import matplotlib as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from biblio import get_dict_champ_vide, score_semantique
from PIL import Image, ImageTk

import io
import os
import re
import PyPDF2

# ======================
# BASE 1 : Mots
# ======================
conn = sqlite3.connect("kabyle_learn.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL UNIQUE
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categorie_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    FOREIGN KEY(categorie_id) REFERENCES categories(id)
)
""")
conn.commit()

# ======================
# BASE 2 : Verbes
# ======================
verb_conn = sqlite3.connect("verbes.db")
verb_cursor = verb_conn.cursor()

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


# ======================
# BASE 3 : Notes
# ======================
note_conn = sqlite3.connect("notes.db")
note_cursor = note_conn.cursor()

note_cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mot_guess INTEGER NOT NULL,
    mot_show INTEGER NOT NULL,
    categorie_id TEXT NOT NULL
)
""")
note_conn.commit()
# ======================

# ======================
# BASE 4 : DICTIONNAIRE APPRENDRE_KABYLE.COM
# ======================
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

# ======================
# BASE 4 : SUJET BAC
# ======================
bac_conn = sqlite3.connect("bac.db")
bac_cur = bac_conn.cursor()
bac_cur.execute("""
CREATE TABLE IF NOT EXISTS bac (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reponse TEXT,
    question BLOB,
    annee INTEGER NOT NULL,
    categorie TEXT NOT NULL
)
""")
bac_conn.commit()

class KabyleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Apprendre le Kabyle")
        self.root.geometry("1000x800") # Taille fixe

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(padx=20, pady=20)

        self.add_button = tk.Button(self.main_frame, text="Ajouter un mot", command=self.ajouter_mot, width=30)
        self.add_button.pack(pady=10)

        self.quiz_button = tk.Button(self.main_frame, text="Démarrer le challenge", command=self.lancer_quiz, width=30)
        self.quiz_button.pack(pady=10)

        self.view_button = tk.Button(self.main_frame, text="Visualiser la base", command=self.visualiser_base, width=30)
        self.view_button.pack(pady=10)

        self.categorie_button = tk.Button(self.main_frame, text="Catégories", command=self.gerer_categories, width=30)
        self.categorie_button.pack(pady=10)

        self.verbe_button = tk.Button(self.main_frame, text="Gérer les verbes", command=self.gerer_verbes, width=30)
        self.verbe_button.pack(pady=10)
        
        self.view_button = tk.Button(self.main_frame, text="Dictionnaire", command=self.visualiser_dico, width=30)
        self.view_button.pack(pady=10)
        
        self.view_button = tk.Button(self.main_frame, text="BAC", command=self.visualiser_bac, width=30)
        self.view_button.pack(pady=10)
        
        self.reload_quizz = False


    # ===============================
    #         PARTIE VERBES
    # ===============================
    def gerer_verbes(self):
        win = tk.Toplevel(self.root)
        win.title("Gestion des verbes")
        win.geometry("400x300")

        btn_add = tk.Button(win, text="Ajouter un verbe", command=self.ajouter_verbe, width=30)
        btn_add.pack(pady=10)

        btn_view = tk.Button(win, text="Voir les verbes", command=self.voir_liste_verbes, width=30)
        btn_view.pack(pady=10)

        self.quiz_verbes_button = tk.Button(win, text="Quiz de conjugaison", command=self.lancer_quiz_verbes, width=30)
        self.quiz_verbes_button.pack(pady=20)
        
        self.quiz_verbes_button = tk.Button(win, text="Quiz par niveau", command=self.quiz_verbe_niveau, width=30)
        self.quiz_verbes_button.pack(pady=30)
    
    def voir_liste_verbes(self):
        liste_win = tk.Toplevel(self.root)
        liste_win.title("Liste des verbes")
        liste_win.geometry("600x400")

        # Frame avec canvas + scrollbar
        container = tk.Frame(liste_win)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Charger les verbes
        verb_cursor.execute("SELECT id, infinitif FROM verbes ORDER BY infinitif")
        verbes = verb_cursor.fetchall()

        for vid, infinitif in verbes:
            frame = tk.Frame(scroll_frame)
            frame.pack(fill="x", pady=2)

            tk.Label(frame, text=infinitif, width=25, anchor="w").pack(side="left", padx=5)
            tk.Button(frame, text="Détail", command=lambda v=vid: self.detail_verbe(v)).pack(side="left", padx=5)
            tk.Button(frame, text="Supprimer", command=lambda v=vid, w=liste_win: self.supprimer_verbe(v, w)).pack(side="left", padx=5)

    def detail_verbe(self, verbe_id):
        # Récupérer colonnes + données
        verb_cursor.execute("PRAGMA table_info(verbes)")
        colonnes = [c[1] for c in verb_cursor.fetchall()]

        verb_cursor.execute("SELECT * FROM verbes WHERE id=?", (verbe_id,))
        verbe_data = verb_cursor.fetchone()

        if not verbe_data:
            messagebox.showerror("Erreur", "Verbe introuvable.")
            return

        # Création de la fenêtre
        self.detail_win = tk.Toplevel(self.root)
        self.detail_win.title(f"Détail - {verbe_data[1]}")
        self.detail_win.geometry("1100x900")

        # Infinitif
        tk.Label(self.detail_win, text="Infinitif :").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Label(self.detail_win, text=verbe_data[colonnes.index("infinitif")], width=30, anchor="w").grid(row=0, column=1, pady=5, sticky="w")

        # Traduction
        tk.Label(self.detail_win, text="Traduction :").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        tk.Label(self.detail_win, text=verbe_data[colonnes.index("traduction")], width=30, anchor="w").grid(row=0, column=3, pady=5, sticky="w")

        personnes = ["1 si.", "2 si.", "3 si. m", "3 si. f", "1 pl.", "2 pl. m", "2 pl. f", "3 pl. m", "3 pl. f"]
        temps = ["Aoriste (impératif)", "Aoriste (futur)", "Prétérit", "Prétérit négatif"]

        # En-têtes colonnes
        for j, t in enumerate(temps):
            tk.Label(self.detail_win, text=t, font=("Arial", 10, "bold")).grid(row=1, column=j+1, padx=5, pady=5)

        # Lignes
        for i, p in enumerate(personnes):
            tk.Label(self.detail_win, text=p).grid(row=i+2, column=0, padx=5, pady=5, sticky="w")
            for j, t in enumerate(temps):
                if t == "Aoriste (impératif)" and (p in ["1 si.", "3 si. m", "3 si. f", "1 pl.", "3 pl. m", "3 pl. f"]):
                    continue

                # Construire le nom de colonne attendu
                col_name = None
                if t == "Aoriste (impératif)":
                    col_name = f"aoriste_imp_{p.replace(' ', '').replace('.', '').replace('m', 'm').replace('f', 'f')}"
                elif t == "Aoriste (futur)":
                    col_name = f"aoriste_fut_{p.replace(' ', '').replace('.', '').replace('m', 'm').replace('f', 'f')}"
                elif t == "Prétérit":
                    col_name = f"preterit_{p.replace(' ', '').replace('.', '').replace('m', 'm').replace('f', 'f')}"
                elif t == "Prétérit négatif":
                    col_name = f"pret_neg_{p.replace(' ', '').replace('.', '').replace('m', 'm').replace('f', 'f')}"

                if col_name in colonnes:
                    val = verbe_data[colonnes.index(col_name)] or ""
                else:
                    val = ""

                tk.Label(self.detail_win, text=val, width=20, anchor="w").grid(row=i+2, column=j+1, padx=5, pady=5)

        # Participes
        participes = [
            ("Participe de l'aoriste :", "part_aoriste"),
            ("Participe du prétérit (positif) :", "part_pret_pos"),
            ("Participe du prétérit (négatif) :", "part_pret_neg")
        ]
        for idx, (label, colname) in enumerate(participes):
            tk.Label(self.detail_win, text=label).grid(row=20+idx, column=0, pady=5, sticky="w")
            val = verbe_data[colonnes.index(colname)] or ""
            tk.Label(self.detail_win, text=val, width=40, anchor="w").grid(row=20+idx, column=1, pady=5, sticky="w")
    
    def ajouter_verbe(self):
        self.verbe_win = tk.Toplevel(self.root)
        self.verbe_win.title("Ajouter un verbe")
        self.verbe_win.geometry("1100x900")

        tk.Label(self.verbe_win, text="Infinitif :").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.infinitif_entry = tk.Entry(self.verbe_win, width=30)
        self.infinitif_entry.grid(row=0, column=1, pady=5, sticky="w")
        
        tk.Label(self.verbe_win, text="Traduction :").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.trad_entry = tk.Entry(self.verbe_win, width=30)
        self.trad_entry.grid(row=0, column=3, pady=5, sticky="w")

        personnes = ["1 si.", "2 si.", "3 si. m", "3 si. f", "1 pl.", "2 pl. m", "2 pl. f", "3 pl. m", "3 pl. f"]
        temps = ["Aoriste (impératif)", "Aoriste (futur)", "Prétérit", "Prétérit négatif"]

        self.entries = {}
        # En-têtes colonnes
        for j, t in enumerate(temps):
            tk.Label(self.verbe_win, text=t, font=("Arial", 10, "bold")).grid(row=1, column=j+1, padx=5, pady=5)

        # Lignes + champs
        for i, p in enumerate(personnes):
            tk.Label(self.verbe_win, text=p).grid(row=i+2, column=0, padx=5, pady=5, sticky="w")
            for j, t in enumerate(temps):
                if t == "Aoriste (impératif)" and (p == "1 si." or p == "3 si. m" or p == "3 si. f" or p == "1 pl." or p == "3 pl. m" or p == "3 pl. f"):
                    continue  # Pas de champs pour ces personnes dans l'impératif
                e = tk.Entry(self.verbe_win, width=20)
                e.grid(row=i+2, column=j+1, padx=5, pady=5)
                self.entries[f"{t}_{p}"] = e

        # Participes
        tk.Label(self.verbe_win, text="Participe de l'aoriste :").grid(row=20, column=0, pady=5, sticky="w")
        self.part_aoriste = tk.Entry(self.verbe_win, width=40)
        self.part_aoriste.grid(row=20, column=1, pady=5, sticky="w")

        tk.Label(self.verbe_win, text="Participe du prétérit (positif) :").grid(row=21, column=0, pady=5, sticky="w")
        self.part_pret_pos = tk.Entry(self.verbe_win, width=40)
        self.part_pret_pos.grid(row=21, column=1, pady=5, sticky="w")

        tk.Label(self.verbe_win, text="Participe du prétérit (négatif) :").grid(row=22, column=0, pady=5, sticky="w")
        self.part_pret_neg = tk.Entry(self.verbe_win, width=40)
        self.part_pret_neg.grid(row=22, column=1, pady=5, sticky="w")

        tk.Button(self.verbe_win, text="Enregistrer", command=self.sauver_verbe).grid(row=23, column=0, columnspan=2, pady=20)

    def sauver_verbe(self):
        infinitif = self.infinitif_entry.get().strip()
        traduction = self.trad_entry.get().strip()
        if not infinitif:
            messagebox.showerror("Erreur", "Veuillez entrer l'infinitif du verbe.")
            return
        if not traduction:
            messagebox.showerror("Erreur", "Veuillez entrer la traduction du verbe.")
            return

        data = [infinitif, traduction]
        for key in self.entries:
            data.append(self.entries[key].get().strip())

        data.append(self.part_aoriste.get().strip())
        data.append(self.part_pret_pos.get().strip())
        data.append(self.part_pret_neg.get().strip())

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
        messagebox.showinfo("Succès", "Verbe ajouté avec succès.")
        self.verbe_win.destroy()

    def supprimer_verbe(self, vid, win):
        if messagebox.askyesno("Confirmation", "Supprimer ce verbe ?"):
            verb_cursor.execute("DELETE FROM verbes WHERE id=?", (vid,))
            verb_conn.commit()
            win.destroy()
            self.gerer_verbes()
    
    # ===============================
    #        QUIZ CONJUGAISON
    # ===============================
    def lancer_quiz_verbes(self):
        try:
            nb_questions = simpledialog.askinteger("Quiz verbes", "Nombre de questions :", minvalue=1, maxvalue=50)
        except:
            return
        if not nb_questions:
            return

        verb_cursor.execute("SELECT * FROM verbes")
        self.tous_les_verbes = verb_cursor.fetchall()
        if not self.tous_les_verbes:
            messagebox.showerror("Erreur", "Aucun verbe dans la base.")
            return

        # Mapping colonnes
        verb_cursor.execute("PRAGMA table_info(verbes)")
        colonnes = [c[1] for c in verb_cursor.fetchall()]

        self.colonnes_conjug = []
        self.map_temps_personne = {}

        for col in colonnes:
            if col in ("id", "infinitif", "traduction", "part_aoriste", "part_pret_pos", "part_pret_neg"):
                continue
            if col.startswith("aoriste_imp"):
                temps = "Aoriste (impératif)"
                personne = col.split("_")[-1]
            elif col.startswith("aoriste_fut"):
                temps = "Aoriste (futur)"
                personne = col.split("_")[-1]
            elif col.startswith("preterit") and not col.startswith("pret_neg"):
                temps = "Prétérit"
                personne = col.split("_")[-1]
            elif col.startswith("pret_neg"):
                temps = "Prétérit négatif"
                personne = col.split("_")[-1]
            else:
                continue
            self.colonnes_conjug.append(col)
            self.map_temps_personne[col] = (temps, personne)

        # Init
        self.nb_questions_total = nb_questions
        self.nb_questions_courantes = 0
        self.score = 0
        self.mauvaises_reponses = []  # On stocke les erreurs

        # Fenêtre quiz
        self.quiz_win = tk.Toplevel(self.root)
        self.quiz_win.title("Quiz de conjugaison (Kabyle)")
        self.quiz_win.geometry("600x300")

        self.lbl_question = tk.Label(self.quiz_win, text="", font=("Arial", 14), wraplength=500)
        self.lbl_question.pack(pady=20)

        self.entry_reponse = tk.Entry(self.quiz_win, font=("Arial", 14))
        self.entry_reponse.pack(pady=10)

        self.btn_valider = tk.Button(self.quiz_win, text="Valider", command=self.verifier_reponse_verbe)
        self.btn_valider.pack(pady=10)

        self.lbl_feedback = tk.Label(self.quiz_win, text="", font=("Arial", 12))
        self.lbl_feedback.pack(pady=10)

        self.nouvelle_question_verbe()


    def nouvelle_question_verbe(self):
        if self.nb_questions_courantes >= self.nb_questions_total:
            self.quiz_win.destroy()
            self.afficher_corrections()
            return

        # Choisir un verbe
        verbe_data = random.choice(self.tous_les_verbes)
        verbe_dict = {}
        verb_cursor.execute("PRAGMA table_info(verbes)")
        cols = [c[1] for c in verb_cursor.fetchall()]
        for col, val in zip(cols, verbe_data):
            verbe_dict[col] = val

        col_conjug = random.choice(self.colonnes_conjug)
        temps, personne = self.map_temps_personne[col_conjug]

        self.question_courante = {
            "infinitif": verbe_dict["infinitif"],
            "traduction": verbe_dict["traduction"],
            "temps": temps,
            "personne": personne,
            "reponse_attendue": verbe_dict[col_conjug] or ""
        }

        self.nb_questions_courantes += 1
        self.lbl_question.config(text=f"Q{self.nb_questions_courantes}/{self.nb_questions_total} :\n"
                                    f"Conjugue le verbe '{self.question_courante['infinitif']}' "
                                    f"({self.question_courante['traduction']})\n"
                                    f"Temps : {temps} | Personne : {personne}")
        self.entry_reponse.delete(0, tk.END)
        self.lbl_feedback.config(text="")


    def verifier_reponse_verbe(self):
        rep = self.entry_reponse.get().strip()
        attendu = self.question_courante["reponse_attendue"]

        if rep.lower() == attendu.lower():
            self.score += 1
        else:
            self.mauvaises_reponses.append({
                "infinitif": self.question_courante["infinitif"],
                "traduction": self.question_courante["traduction"],
                "temps": self.question_courante["temps"],
                "personne": self.question_courante["personne"],
                "votre_reponse": rep,
                "bonne_reponse": attendu
            })

        self.nouvelle_question_verbe()


    def afficher_corrections(self):
        if not self.mauvaises_reponses:
            messagebox.showinfo("Résultat", f"Bravo ! Tout est correct.\nScore : {self.score}/{self.nb_questions_total}")
            return

        self.index_correction = 0

        self.corr_win = tk.Toplevel(self.root)
        self.corr_win.title("Corrections")
        self.corr_win.geometry("600x300")

        self.lbl_corr = tk.Label(self.corr_win, text="", font=("Arial", 12), wraplength=500)
        self.lbl_corr.pack(pady=20)

        btn_frame = tk.Frame(self.corr_win)
        btn_frame.pack()

        tk.Button(btn_frame, text="⬅ Précédent", command=self.corr_prev).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Suivant ➡", command=self.corr_next).pack(side="left", padx=5)

        self.afficher_correction_courante()

    def afficher_correction_courante(self):
        if not self.mauvaises_reponses:
            return
        corr = self.mauvaises_reponses[self.index_correction]
        self.lbl_corr.config(
            text=(f"Erreur {self.index_correction+1}/{len(self.mauvaises_reponses)}\n\n"
                f"Verbe : {corr['infinitif']} ({corr['traduction']})\n"
                f"Temps : {corr['temps']} | Personne : {corr['personne']}\n\n"
                f"Votre réponse : {corr['votre_reponse']}\n"
                f"Bonne réponse : {corr['bonne_reponse']}")
        )

    def corr_prev(self):
        if self.index_correction > 0:
            self.index_correction -= 1
            self.afficher_correction_courante()


    def corr_next(self):
        if self.index_correction < len(self.mauvaises_reponses) - 1:
            self.index_correction += 1
            self.afficher_correction_courante()
    
    def quiz_verbe_niveau(self):
        self.verbe_niv = tk.Toplevel(self.root)
        self.verbe_niv.title("Choisir un niveau de quizz")
        self.verbe_niv.geometry("600x400")
        
        tk.Label(self.verbe_niv, text="Choisissez un niveau de quizz :", font=("Arial", 14)).pack(pady=20)
        niveaux = ["Débutant", "Intermédiaire", "Avancé"]
        for niveau in niveaux:
            btn = tk.Button(self.verbe_niv, text=niveau, command=lambda n=niveau: self.lancer_quiz_niveau(n), width=20)
            btn.pack(pady=10)
    
    def lancer_quiz_niveau(self, niveau):
        verb_cursor.execute("SELECT * FROM verbes")
        verbes = verb_cursor.fetchall()
        
        if not verbes:
            messagebox.showerror("Erreur", "Aucun verbe dans la base.")
            return

        self.win_quiz_niv = tk.Toplevel(self.root)
        self.win_quiz_niv.title(f"Quiz verbes - Niveau {niveau}")
        self.win_quiz_niv.geometry("1100x900")
        
        verbe = random.choice(verbes)
        print(verbe)

        if niveau == "Avancé":
            tk.Label(self.win_quiz_niv, text="Infinitif :").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.infinitif_entry = tk.Entry(self.win_quiz_niv, width=30)
            self.infinitif_entry.grid(row=0, column=1, pady=5, sticky="w")
        
            tk.Label(self.win_quiz_niv, text="Traduction :").grid(row=0, column=2, padx=5, pady=5, sticky="w")
            self.trad_entry = tk.Entry(self.win_quiz_niv, width=30)
            self.trad_entry.grid(row=0, column=3, pady=5, sticky="w")
        else:
            tk.Label(self.win_quiz_niv, text="Infinitif :").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            tk.Label(self.win_quiz_niv, text=verbe[1], width=30, anchor="w").grid(row=0, column=1, pady=5, sticky="w")
            tk.Label(self.win_quiz_niv, text="Traduction :").grid(row=0, column=2, padx=5, pady=5, sticky="w")
            tk.Label(self.win_quiz_niv, text=verbe[2], width=30, anchor="w").grid(row=0, column=3, pady=5, sticky="w")
        
            
        personnes = ["1 si.", "2 si.", "3 si. m", "3 si. f", "1 pl.", "2 pl. m", "2 pl. f", "3 pl. m", "3 pl. f"]
        temps = ["Aoriste (impératif)", "Aoriste (futur)", "Prétérit", "Prétérit négatif"]
        
        dict_rep, champs_vides = get_dict_champ_vide(niveau, verbe)
        
        for champ in champs_vides:
            print(f"{champ}: {dict_rep[champ]}")

        self.entries = {}
        # En-têtes colonnes
        for j, t in enumerate(temps):
            tk.Label(self.win_quiz_niv, text=t, font=("Arial", 10, "bold")).grid(row=1, column=j+1, padx=5, pady=5)

        # Lignes + champs
        for i, p in enumerate(personnes):
            tk.Label(self.win_quiz_niv, text=p).grid(row=i+2, column=0, padx=5, pady=5, sticky="w")
            for j, t in enumerate(temps):
                if t == "Aoriste (impératif)" and (p == "1 si." or p == "3 si. m" or p == "3 si. f" or p == "1 pl." or p == "3 pl. m" or p == "3 pl. f"):
                    continue  # Pas de champs pour ces personnes dans l'impératif
                if f"{t}_{p}" in champs_vides:
                    e = tk.Entry(self.win_quiz_niv, width=20)
                    e.grid(row=i+2, column=j+1, padx=5, pady=5)
                    self.entries[f"{t}_{p}"] = e
                else:
                    val = dict_rep[f"{t}_{p}"]
                    tk.Label(self.win_quiz_niv, text=val, width=20, anchor="w").grid(row=i+2, column=j+1, padx=5, pady=5)

        # Participes
        tk.Label(self.win_quiz_niv, text="Participe de l'aoriste :").grid(row=20, column=0, pady=5, sticky="w")
        if "part_aoriste" in champs_vides:
            self.part_aoriste = tk.Entry(self.win_quiz_niv, width=40)
            self.part_aoriste.grid(row=20, column=1, pady=5, sticky="w")
        else:
            val = dict_rep["part_aoriste"]
            tk.Label(self.win_quiz_niv, text=val, width=40, anchor="w").grid(row=20, column=1, pady=5, sticky="w")

        tk.Label(self.win_quiz_niv, text="Participe du prétérit (positif) :").grid(row=21, column=0, pady=5, sticky="w")
        if "part_pret_pos" in champs_vides:
            self.part_pret_pos = tk.Entry(self.win_quiz_niv, width=40)
            self.part_pret_pos.grid(row=21, column=1, pady=5, sticky="w")
        else:
            val = dict_rep["part_pret_pos"]
            tk.Label(self.win_quiz_niv, text=val, width=40, anchor="w").grid(row=21, column=1, pady=5, sticky="w")

        tk.Label(self.win_quiz_niv, text="Participe du prétérit (négatif) :").grid(row=22, column=0, pady=5, sticky="w")
        if "part_pret_neg" in champs_vides:
            self.part_pret_neg = tk.Entry(self.win_quiz_niv, width=40)
            self.part_pret_neg.grid(row=22, column=1, pady=5, sticky="w")
        else:
            val = dict_rep["part_pret_neg"]
            tk.Label(self.win_quiz_niv, text=val, width=40, anchor="w").grid(row=22, column=1, pady=5, sticky="w")

        tk.Button(self.win_quiz_niv, text="Soumettre", command=lambda: self.verif_quiz_verbe_niv(verbe, niveau, dict_rep, champs_vides)).grid(row=23, column=0, columnspan=2, pady=20)
    
    def verif_quiz_verbe_niv(self, verbe, niveau, dict_rep, champs_vides):
        bonnes_reponses = 0
        total = len(champs_vides)

        # Vérifier les champs des conjugaisons
        for champ in champs_vides:
            if champ in self.entries:
                entry = self.entries[champ]
                user_answer = entry.get().strip()
                bonne_reponse = dict_rep[champ].strip()

                if user_answer.lower() == bonne_reponse.lower():
                    bonnes_reponses += 1
                    entry.config(bg="lightgreen")
                else:
                    entry.config(bg="salmon")
                    # Afficher la correction juste à droite
                    row, col = entry.grid_info()["row"], entry.grid_info()["column"]
                    tk.Label(self.win_quiz_niv, text=f"✔ {bonne_reponse}", fg="blue", anchor="w").grid(row=row, column=col+1, padx=5, sticky="w")

        # Vérifier participe aoriste
        if "part_aoriste" in champs_vides:
            rep = self.part_aoriste.get().strip()
            if rep.lower() == dict_rep["part_aoriste"].lower():
                bonnes_reponses += 1
                self.part_aoriste.config(bg="lightgreen")
            else:
                self.part_aoriste.config(bg="salmon")
                row, col = self.part_aoriste.grid_info()["row"], self.part_aoriste.grid_info()["column"]
                tk.Label(self.win_quiz_niv, text=f"✔ {dict_rep['part_aoriste']}", fg="blue", anchor="w").grid(row=row, column=col+1, padx=5, sticky="w")

        # Vérifier participe prétérit positif
        if "part_pret_pos" in champs_vides:
            rep = self.part_pret_pos.get().strip()
            if rep.lower() == dict_rep["part_pret_pos"].lower():
                bonnes_reponses += 1
                self.part_pret_pos.config(bg="lightgreen")
            else:
                self.part_pret_pos.config(bg="salmon")
                row, col = self.part_pret_pos.grid_info()["row"], self.part_pret_pos.grid_info()["column"]
                tk.Label(self.win_quiz_niv, text=f"✔ {dict_rep['part_pret_pos']}", fg="blue", anchor="w").grid(row=row, column=col+1, padx=5, sticky="w")

        # Vérifier participe prétérit négatif
        if "part_pret_neg" in champs_vides:
            rep = self.part_pret_neg.get().strip()
            if rep.lower() == dict_rep["part_pret_neg"].lower():
                bonnes_reponses += 1
                self.part_pret_neg.config(bg="lightgreen")
            else:
                self.part_pret_neg.config(bg="salmon")
                row, col = self.part_pret_neg.grid_info()["row"], self.part_pret_neg.grid_info()["column"]
                tk.Label(self.win_quiz_niv, text=f"✔ {dict_rep['part_pret_neg']}", fg="blue", anchor="w").grid(row=row, column=col+1, padx=5, sticky="w")

        # Résumé final
        score = f"Score : {bonnes_reponses}/{total}"
        if bonnes_reponses == total:
            messagebox.showinfo("Résultat", score + "\n\nExcellent !")
        else:
            messagebox.showwarning("Résultat", score + "\n\nRegarde les corrections en bleu.")


        
    def ajouter_mot(self, categorie_id=None):
        francais = simpledialog.askstring("Ajout de mot", "Mot en français :")
        if not francais:
            return
        kabyle = simpledialog.askstring("Ajout de mot", "Traduction en kabyle :")
        if not kabyle:
            return

        francais = francais.strip().lower()
        kabyle = kabyle.strip().lower()

        cursor.execute("SELECT * FROM mots WHERE francais = ? OR kabyle = ?", (francais, kabyle))
        exist = cursor.fetchone()

        if exist:
            messagebox.showwarning("Doublon détecté", "Ce mot existe déjà en français ou en kabyle.\nAjout annulé.")
            return

        cursor.execute("INSERT INTO mots (francais, kabyle, categorie_id) VALUES (?, ?, ?)", (francais, kabyle, categorie_id))
        conn.commit()
        messagebox.showinfo("Succès", f"Mot '{francais}' ajouté avec succès.")
        if categorie_id:
            self.ouvrir_categorie(categorie_id, self.get_nom_categorie(categorie_id))


    def visualiser_base(self, categorie_id=None):
        # Récupération des mots
        if categorie_id:
            cursor.execute("SELECT id, francais, kabyle FROM mots WHERE categorie_id = ?", (categorie_id,))
        else:
            cursor.execute("SELECT id, francais, kabyle FROM mots")
        mots = cursor.fetchall()
        total = len(mots)

        if total == 0:
            messagebox.showinfo("Base vide", "Aucun mot dans la base.")
            return

        view_window = tk.Toplevel(self.root)
        view_window.title("Visualisation de la base")
        view_window.geometry("1000x800")

        label_total = tk.Label(view_window, text=f"Nombre total de mots : {total}", font=("Arial", 10))
        label_total.pack(pady=10)

        # Scrollable area
        canvas = tk.Canvas(view_window, width=960, height=700)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(view_window, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        frame_in_canvas = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame_in_canvas, anchor="nw")

        # En-tête
        header = tk.Frame(frame_in_canvas)
        header.pack(pady=5)
        tk.Label(header, text="Français", width=30, font=("Arial", 10, "bold"), anchor="w").grid(row=0, column=0, padx=5)
        tk.Label(header, text="Kabyle", width=30, font=("Arial", 10, "bold"), anchor="w").grid(row=0, column=1, padx=5)
        tk.Label(header, text="Action", width=15, font=("Arial", 10, "bold"), anchor="center").grid(row=0, column=2, padx=5)
        tk.Label(header, text="Modifier", width=15, font=("Arial", 10, "bold"), anchor="center").grid(row=0, column=3, padx=5)

        # Lignes
        for mot_id, fr, kab in mots:
            ligne = tk.Frame(frame_in_canvas)
            ligne.pack(anchor="w", pady=2)

            tk.Label(ligne, text=fr, width=30, font=("Arial", 10), anchor="w").grid(row=0, column=0, padx=5)
            tk.Label(ligne, text=kab, width=30, font=("Arial", 10), anchor="w").grid(row=0, column=1, padx=5)

            btn_supprimer = tk.Button(ligne, text="Supprimer", font=("Arial", 9),
                                    command=lambda mid=mot_id, win=view_window, cid=categorie_id: self.supprimer_mot(mid, win, cid))
            btn_supprimer.grid(row=0, column=2, padx=5)
            
            btn_modifier = tk.Button(
            ligne, text="Modifier", font=("Arial", 9),
            command=lambda mid=mot_id, fr=fr, kab=kab, win=view_window, cid=categorie_id: self.modifier_mot(mid, fr, kab, win, cid)
            )
            btn_modifier.grid(row=0, column=3, padx=5)
            
    def modifier_mot(self, mot_id, fr, kab, fenetre_actuelle, categorie_id=None):
        # Ouvrir une fenêtre popup pour modifier
        new_fr = simpledialog.askstring("Modifier mot", "Mot en français :", initialvalue=fr)
        if not new_fr:
            return
        new_kab = simpledialog.askstring("Modifier mot", "Traduction en kabyle :", initialvalue=kab)
        if not new_kab:
            return

        new_fr = new_fr.strip().lower()
        new_kab = new_kab.strip().lower()

        # Vérifier si le nouveau mot existe déjà ailleurs
        cursor.execute(
            "SELECT id FROM mots WHERE (francais = ? OR kabyle = ?) AND id != ?",
            (new_fr, new_kab, mot_id)
        )
        if cursor.fetchone():
            messagebox.showwarning("Doublon détecté", "Ce mot existe déjà.\nModification annulée.")
            return

        # Mettre à jour la base
        cursor.execute(
            "UPDATE mots SET francais = ?, kabyle = ? WHERE id = ?",
            (new_fr, new_kab, mot_id)
        )
        conn.commit()
        messagebox.showinfo("Succès", "Mot modifié avec succès.")

        fenetre_actuelle.destroy()
        self.visualiser_base(categorie_id)

            
    def supprimer_mot(self, mot_id, fenetre_actuelle, categorie_id=None):
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce mot ?"):
            cursor.execute("DELETE FROM mots WHERE id = ?", (mot_id,))
            conn.commit()
            messagebox.showinfo("Succès", "Mot supprimé avec succès.")
            fenetre_actuelle.destroy()
            self.visualiser_base(categorie_id)

    def lancer_quiz(self, categorie_id=None):
        if categorie_id:
            cursor.execute("SELECT francais, kabyle FROM mots WHERE categorie_id = ?", (categorie_id,))
            self.current_categorie = categorie_id
        else:
            cursor.execute("SELECT francais, kabyle FROM mots")

        mots = cursor.fetchall()
        self.save_quiz = {}

        if len(mots) == 0:
            messagebox.showwarning("Aucun mot", "Ajoute des mots avant de démarrer le challenge.")
            return

        nb_questions = simpledialog.askinteger("Taille du quiz", "Combien de mots pour ce quiz ?", minvalue=1)

        if nb_questions is None:
            return

        total_mots = len(mots)
        if nb_questions >= total_mots:
            self.quiz_mots = random.sample(mots, len(mots))
            info = f"Base contient {total_mots} mots. Quiz avec {total_mots} mots."
        else:
            self.quiz_mots = random.sample(mots, nb_questions)
            info = f"Quiz avec {nb_questions} mots aléatoires."

        messagebox.showinfo("Challenge", info)

        self.current_index = 0
        self.score = 0
        self.erreurs = []

        self.quiz_frame = tk.Toplevel(self.root)
        self.quiz_frame.title("Challenge Kabyle")
        self.quiz_frame.geometry("1000x800")

        self.label_question = tk.Label(self.quiz_frame, text="", font=("Arial", 10))
        self.label_question.pack(pady=20)

        self.entry_reponse = tk.Entry(self.quiz_frame, font=("Arial", 10))
        self.entry_reponse.pack(pady=10)
        self.entry_reponse.bind("<Return>", self.valider_reponse)

        self.bouton_valider = tk.Button(self.quiz_frame, text="Valider", command=self.valider_reponse, font=("Arial", 10))
        self.bouton_valider.pack(pady=10)

        self.next_question()
    
    def relancer_quizz(self):        
        if len(self.save_quiz) < 0:
            print("erreur, aucun quizz n'a été save")
            return
        
        self.recap_window.destroy()
        print(self.save_quiz)
        
        self.reload_quizz = True
        self.current_index = 0
        self.score = 0
        self.erreurs = []
        
        # recréer une nouvelle fenêtre quiz
        self.quiz_frame = tk.Toplevel(self.root)
        self.quiz_frame.title("Challenge Kabyle (Relancé)")
        self.quiz_frame.geometry("1000x800")

        self.label_question = tk.Label(self.quiz_frame, text="", font=("Arial", 10))
        self.label_question.pack(pady=20)

        self.entry_reponse = tk.Entry(self.quiz_frame, font=("Arial", 10))
        self.entry_reponse.pack(pady=10)
        self.entry_reponse.bind("<Return>", self.valider_reponse)

        self.bouton_valider = tk.Button(self.quiz_frame, text="Valider", command=self.valider_reponse, font=("Arial", 10))
        self.bouton_valider.pack(pady=10)
        
        self.index_question = [i for i in range(len(self.quiz_mots))]

        self.next_question()

    def next_question(self):
        if self.current_index >= len(self.quiz_mots):
            self.fin_quiz()
            return

        mot_fr, mot_kab = self.quiz_mots[self.current_index]

        if not self.reload_quizz:
            if random.choice([True, False]):
                self.question = mot_fr
                self.reponse_attendue = mot_kab
                self.label_question.config(text=f"Traduction en Kabyle de : {mot_fr}")
            else:
                self.question = mot_kab
                self.reponse_attendue = mot_fr
                self.label_question.config(text=f"Traduction en Français de : {mot_kab}")
                
            self.save_quiz[self.current_index] = (
                self.question, 
                self.reponse_attendue, 
                self.label_question.cget("text")
            )
        else:
            index = random.choice(self.index_question)
            self.question, self.reponse_attendue, question_txt = self.save_quiz[index]
            self.label_question.config(text=question_txt)
            
            self.index_question.remove(index)
            
        self.entry_reponse.delete(0, tk.END)

    def valider_reponse(self, event=None):
        user_input = self.entry_reponse.get().strip().lower()
        if user_input == self.reponse_attendue.lower():
            self.score += 1
        else:
            self.erreurs.append({
                "question": self.question,
                "ta_reponse": user_input,
                "bonne_reponse": self.reponse_attendue
            })

        self.current_index += 1
        self.next_question()

    def fin_quiz(self):
        total = len(self.quiz_mots)
        self.quiz_frame.destroy()

        if not self.erreurs:
            messagebox.showinfo("Résultat", f"Votre score : {self.score}/{total}\nBravo ! Aucune erreur.")
            return

        if not self.reload_quizz:
            note_cursor.execute("""
            INSERT INTO notes (categorie_id, mot_guess, mot_show)
            VALUES (?, ?, ?)
            """, (self.current_categorie, self.score, total))
            note_conn.commit()
        
        self.recap_index = 0
        self.recap_window = tk.Toplevel(self.root)
        self.recap_window.title("Révision des erreurs")
        self.recap_window.geometry("1000x800")

        self.label_score = tk.Label(self.recap_window, text=f"Votre score : {self.score}/{total}", font=("Arial", 10))
        self.label_score.pack(pady=10)

        self.label_erreur = tk.Label(self.recap_window, text="", font=("Arial", 10), wraplength=950, justify="left")
        self.label_erreur.pack(pady=20)

        btn_frame = tk.Frame(self.recap_window)
        btn_frame.pack()
        
        self.btn_relancer = tk.Button(btn_frame, text="Relancer le quiz", font=("Arial", 10), command=self.relancer_quizz)
        self.btn_relancer.pack(pady=30)

        self.btn_prev = tk.Button(btn_frame, text="⟵ Précédent", command=self.prev_error, state=tk.DISABLED, font=("Arial", 10))
        self.btn_prev.pack(side=tk.LEFT, padx=10)

        self.btn_next = tk.Button(btn_frame, text="Suivant ⟶", command=self.next_error, font=("Arial", 10))
        self.btn_next.pack(side=tk.LEFT, padx=10)
        
        self.show_error()

    def show_error(self):
        err = self.erreurs[self.recap_index]
        texte = f"Question : {err['question']}\n\nTa réponse : {err['ta_reponse']}\nBonne réponse : {err['bonne_reponse']}"
        self.label_erreur.config(text=texte)

        if self.recap_index == 0:
            self.btn_prev.config(state=tk.DISABLED)
        else:
            self.btn_prev.config(state=tk.NORMAL)

        if self.recap_index == len(self.erreurs) - 1:
            self.btn_next.config(text="Terminer", command=self.finish_recap)
        else:
            self.btn_next.config(text="Suivant ⟶", command=self.next_error)

    def next_error(self):
        if self.recap_index < len(self.erreurs) - 1:
            self.recap_index += 1
            self.show_error()

    def prev_error(self):
        if self.recap_index > 0:
            self.recap_index -= 1
            self.show_error()
            
    def finish_recap(self):
        self.recap_window.destroy()
        self.reload_quizz = False
        self.save_quiz = {}
    
    def visualiser_stats(self, categorie_id):
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Statistiques de la catégorie")
        stats_window.geometry("700x700")

        note_cursor.execute("SELECT mot_guess, mot_show FROM notes WHERE categorie_id = ?", (categorie_id,))
        notes = note_cursor.fetchall()

        if not notes:
            nb_quizzes = 0
            total_score = 0
            total_questions = 0
            avg_score = 0
            avg_questions = 0
        else:
            total_score = sum(note[0] for note in notes)
            total_questions = sum(note[1] for note in notes)
            nb_quizzes = len(notes)

            avg_score = total_score * 100 / total_questions if nb_quizzes > 0 else 0
            avg_questions = total_questions / nb_quizzes if nb_quizzes > 0 else 0

        tk.Label(stats_window, text=f"Nombre de quizzes : {nb_quizzes}", font=("Arial", 10)).pack(pady=5)
        tk.Label(stats_window, text=f"Score total : {total_score}", font=("Arial", 10)).pack(pady=5)
        tk.Label(stats_window, text=f"Questions totales : {total_questions}", font=("Arial", 10)).pack(pady=5)
        tk.Label(stats_window, text=f"Score moyen : {avg_score:.2f}%", font=("Arial", 10)).pack(pady=5)
        tk.Label(stats_window, text=f"Questions moyennes par quiz : {avg_questions:.2f}", font=("Arial", 10)).pack(pady=5)

        # Conversion des scores en pourcentage
        scores_pct = [(note[0] / note[1]) * 100 for note in notes]

        if notes:
            # Création de la figure matplotlib
            fig = Figure(figsize=(5, 3), dpi=100)
            ax = fig.add_subplot(111)

            # Tracer la courbe des scores (sans points, juste une ligne lisse)
            ax.plot(range(1, len(scores_pct) + 1), scores_pct, linestyle='-', linewidth=2, color="royalblue")

            # Mise en forme
            ax.set_title("Évolution des scores (%)", fontsize=12)
            ax.set_xlabel("Quiz")
            ax.set_ylabel("Score (%)")
            ax.set_ylim(0, 100)  # Toujours sur 100 car pourcentage
            ax.grid(True, linestyle="--", alpha=0.6)

            # Affichage dans Tkinter
            canvas = FigureCanvasTkAgg(fig, master=stats_window)
            canvas.get_tk_widget().pack(pady=10)
            canvas.draw()

        # Bouton pour fermer
        tk.Button(stats_window, text="Fermer", command=stats_window.destroy, font=("Arial", 10)).pack(pady=10)
        tk.Button(stats_window, text="reinitialiser les données", command=lambda: self.reset_data(categorie_id, stats_window), font=("Arial", 10)).pack(pady=20)
    
    def reset_data(self, categorie_id, stats_window):
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment réinitialiser les données de cette catégorie ?"):
            note_cursor.execute("DELETE FROM notes WHERE categorie_id = ?", (categorie_id,))
            note_conn.commit()
            messagebox.showinfo("Succès", "Données réinitialisées avec succès.")
            
            stats_window.destroy()
            
            self.visualiser_stats(categorie_id)

    def gerer_categories(self):
        self.cat_window = tk.Toplevel(self.root)
        self.cat_window.title("Catégories")
        self.cat_window.geometry("1000x600")

        btn_new_cat = tk.Button(self.cat_window, text="Créer une nouvelle catégorie", command=self.creer_categorie, font=("Arial", 10))
        btn_new_cat.pack(pady=10)

        self.liste_categories()

    def creer_categorie(self):
        titre = simpledialog.askstring("Nouvelle catégorie", "Titre de la catégorie :")
        if not titre:
            return
        titre = titre.strip().lower()

        try:
            cursor.execute("INSERT INTO categories (titre) VALUES (?)", (titre,))
            conn.commit()
            messagebox.showinfo("Succès", f"Catégorie '{titre}' créée.")
            self.liste_categories()
        except sqlite3.IntegrityError:
            messagebox.showwarning("Erreur", "Cette catégorie existe déjà.")

    def liste_categories(self):
        for widget in self.cat_window.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") not in ["Créer une nouvelle catégorie"]:
                widget.destroy()

        cursor.execute("SELECT id, titre FROM categories")
        categories = cursor.fetchall()

        for cat_id, titre in categories:
            btn = tk.Button(self.cat_window, text=titre.capitalize(), font=("Arial", 10),
                            command=lambda cid=cat_id, t=titre: self.ouvrir_categorie(cid, t))
            btn.pack(pady=5)

    def ouvrir_categorie(self, cat_id, titre):
        self.current_categorie = cat_id
        cat_frame = tk.Toplevel(self.root)
        cat_frame.title(f"Catégorie : {titre}")
        cat_frame.geometry("1000x800")
        
        self.fenetre_categorie_active = cat_frame

        label = tk.Label(cat_frame, text=f"Catégorie : {titre}", font=("Arial", 12, "bold"))
        label.pack(pady=10)

        btn_add = tk.Button(cat_frame, text="Ajouter plusieurs mots", font=("Arial", 10),
                    command=lambda: self.ajouter_mots_multiples(cat_id))
        btn_add.pack(pady=10)

        btn_quiz = tk.Button(cat_frame, text="Démarrer le challenge", font=("Arial", 10),
                             command=lambda: self.lancer_quiz(cat_id))
        btn_quiz.pack(pady=10)

        btn_view = tk.Button(cat_frame, text="Voir les mots", font=("Arial", 10),
                             command=lambda: self.visualiser_base(cat_id))
        btn_view.pack(pady=10)
        
        btn_view_stats = tk.Button(cat_frame, text="Voir les statistiques", font=("Arial", 10),
                                  command=lambda: self.visualiser_stats(cat_id))
        btn_view_stats.pack(pady=10)
    
    def ajouter_mots_multiples(self, categorie_id=None):
        self.multi_window = tk.Toplevel(self.root)
        self.multi_window.title("Ajouter plusieurs mots")
        self.multi_window.geometry("1000x800")

        top_frame = tk.Frame(self.multi_window)
        top_frame.pack(pady=10)

        tk.Label(top_frame, text="Nombre de lignes :", font=("Arial", 10)).pack(side="left", padx=5)
        self.nb_lignes_var = tk.IntVar(value=10)
        tk.Spinbox(top_frame, from_=1, to=100, textvariable=self.nb_lignes_var, width=5).pack(side="left")

        tk.Button(top_frame, text="Générer les champs", font=("Arial", 10),
                command=self.generer_champs_mots).pack(side="left", padx=10)

        self.entries_frame = tk.Frame(self.multi_window)
        self.entries_frame.pack(pady=10, fill="both", expand=True)

        # Enregistrement
        self.save_button = tk.Button(self.multi_window, text="Enregistrer", font=("Arial", 10),
                                    command=lambda: self.enregistrer_mots_grille(categorie_id))
        self.save_button.pack(pady=20)

    def generer_champs_mots(self):
        for widget in self.entries_frame.winfo_children():
            widget.destroy()

        self.entrees_francais = []
        self.entrees_kabyle = []

        # Création du canvas avec scrollbar
        canvas = tk.Canvas(self.entries_frame, width=950, height=600)
        scrollbar = tk.Scrollbar(self.entries_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # En-tête
        header = tk.Frame(scrollable_frame)
        header.pack(pady=5)

        tk.Label(header, text="Français", font=("Arial", 10, "bold"), width=40).grid(row=0, column=0, padx=5)
        tk.Label(header, text="Kabyle", font=("Arial", 10, "bold"), width=40).grid(row=0, column=1, padx=5)

        # Champs dynamiques
        nb = self.nb_lignes_var.get()
        for i in range(nb):
            ligne = tk.Frame(scrollable_frame)
            ligne.pack(pady=2)

            entry_fr = tk.Entry(ligne, font=("Arial", 10), width=40)
            entry_fr.grid(row=0, column=0, padx=5)
            self.entrees_francais.append(entry_fr)

            entry_kab = tk.Entry(ligne, font=("Arial", 10), width=40)
            entry_kab.grid(row=0, column=1, padx=5)
            self.entrees_kabyle.append(entry_kab)


    def enregistrer_mots_grille(self, categorie_id=None):
        ajoutés, doublons, erreurs = 0, 0, 0

        for fr_entry, kab_entry in zip(self.entrees_francais, self.entrees_kabyle):
            fr = fr_entry.get().strip().lower()
            kab = kab_entry.get().strip().lower()

            if not kab:
                erreurs += 1
                continue

            cursor.execute("SELECT * FROM mots WHERE francais = ? OR kabyle = ?", (fr, kab))
            if cursor.fetchone():
                doublons += 1
                continue

            cursor.execute("INSERT INTO mots (francais, kabyle, categorie_id) VALUES (?, ?, ?)",
                        (fr, kab, categorie_id))
            ajoutés += 1

        conn.commit()

        msg = f"{ajoutés} mot(s) ajouté(s).\n"
        if doublons:
            msg += f"{doublons} doublon(s) ignoré(s).\n"
        if erreurs:
            msg += f"{erreurs} mot(s) ignoré(s) (pas de traduction kabyle)."

        messagebox.showinfo("Résultat", msg)
        self.multi_window.destroy()

        if categorie_id:
            self.ouvrir_categorie(categorie_id, self.get_nom_categorie(categorie_id))
    
    def visualiser_dico_from_lettre(self, lettre, listbox):
        listbox.delete(0, tk.END)
        base_dico_cursor.execute("SELECT mot_fr, mot_kabyle FROM dico")
        resultats = base_dico_cursor.fetchall()
        for mot in resultats:
            #listbox.insert(tk.END, mot[0])
            if mot[0].startswith(lettre):
                listbox.insert(tk.END, f"{mot[0]} - {mot[1]}")
    
    def visualiser_dico(self):
        dico_window = tk.Toplevel(self.root)
        dico_window.title("Visualisation de la base")
        dico_window.geometry("1000x800")

        # zone d’affichage des mots
        listbox = tk.Listbox(dico_window, width=50, height=40, font=("Arial", 11))
        listbox.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # zone des boutons
        frame_btns = tk.Frame(dico_window)
        frame_btns.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        for lettre in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            tk.Button(
                frame_btns, 
                text=lettre, 
                width=5, 
                font=("Arial", 9), 
                command=lambda l=lettre: self.visualiser_dico_from_lettre(l, listbox)
            ).pack(pady=2)

    def visualiser_bac(self):
        bac_win = tk.Toplevel(self.root)
        bac_win.title("Visualisation des sujets de BAC")
        bac_win.geometry("600x800")
        
        padding_x = 20
        
        col_normaux = 0
        rn = 0
        col_question = 5
        rq = 0
        col_rattrapage = 10
        rr = 0
        for sujet in os.listdir("BAC"):
            sujet_name = sujet.replace(".pdf", "")
            if "kab" in sujet_name:
                if rn == 0:
                    ln = tk.Label(bac_win, text="Traduction d'un texte", width=20, font=("Arial", 9))
                    ln.grid(row=rn, column=col_normaux, padx=padding_x, pady=5, sticky="w")
                    rn += 1
                btn = tk.Button(bac_win, text=sujet_name, width=20, font=("Arial", 9), command=lambda s=sujet_name, cat="normal": self.ouvrir_sujet_bac(s, cat))
                btn.grid(row=rn, column=col_normaux, padx=padding_x, pady=5, sticky="w")
                rn += 1
            elif "question" in sujet_name:
                if rq == 0:
                    lq = tk.Label(bac_win, text="répondre à des questions", width=20, font=("Arial", 9))
                    lq.grid(row=rq, column=col_question, padx=padding_x, pady=5, sticky="w")
                    rq += 1
                btn = tk.Button(bac_win, text=sujet_name, width=20, font=("Arial", 9), command=lambda s=sujet_name, cat="questions": self.ouvrir_sujet_bac(s, cat))
                btn.grid(row=rq, column=col_question, padx=padding_x, pady=5, sticky="w")
                rq += 1
            elif "rattrapage" in sujet_name:
                if rr == 0:
                    lr = tk.Label(bac_win, text="Traduction d'un texte (rattrapage)", width=30, font=("Arial", 9))
                    lr.grid(row=rr, column=col_rattrapage, padx=padding_x, pady=5, sticky="w")
                    rr += 1
                btn = tk.Button(bac_win, text=sujet_name, width=20, font=("Arial", 9), command=lambda s=sujet_name, cat="rattrapage": self.ouvrir_sujet_bac(s, cat))
                btn.grid(row=rr, column=col_rattrapage, padx=padding_x, pady=5, sticky="w")
                rr += 1
            
    def ouvrir_sujet_bac(self, sujet, cat):
        match = re.search(r"\d{4}", sujet)  # récupère une année (4 chiffres)
        if match:
            annee = int(match.group())
            bac_cur.execute(
                "SELECT reponse, question FROM bac WHERE annee = ? AND categorie = ?", 
                (annee, cat)
            )
        correspondance = bac_cur.fetchone()
        if correspondance is None:
            return
        
        bonne_reponse, img_bytes = correspondance
        sujet_win = tk.Toplevel(self.root)
        sujet_win.title(f"Sujet {annee} ({cat})")
        sujet_win.geometry("800x800")
        
        image = Image.open(io.BytesIO(img_bytes))
        image = image.resize((600, 400), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        
        lbl_img = tk.Label(sujet_win, image=photo)
        lbl_img.image = photo  # garder une référence pour éviter que l’image disparaisse
        lbl_img.pack(pady=10)
        
        lbl_txt = tk.Label(sujet_win, text="Votre réponse :", font=("Arial", 12))
        lbl_txt.pack()

        frame_txt = tk.Frame(sujet_win)
        frame_txt.pack(pady=5)

        scrollbar = tk.Scrollbar(frame_txt)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        txt_answer = tk.Text(frame_txt, height=15, width=80, yscrollcommand=scrollbar.set, wrap="word")
        txt_answer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=txt_answer.yview)
        
        def soumettre():
            nonlocal nb_essaie
            nb_essaie += 1
            rep_joueur = txt_answer.get("1.0", tk.END).strip()
            if not rep_joueur:
                messagebox.showwarning("Attention", "Veuillez entrer une réponse.")
                return
            
            lbl_load = tk.Label(sujet_win, text="Calcul du score...", width=100, font=("Arial", 9))
            lbl_load.pack()
            sujet_win.update_idletasks()
            
            score = score_semantique(rep_joueur, bonne_reponse)
            lbl_load.config(text=f"Essaie numéro {nb_essaie}, score de: {score} / 20")
        
        nb_essaie = 0
        btn = tk.Button(sujet_win, text="Soumettre", width=20, font=("Arial", 9), command=soumettre).pack()
    


if __name__ == "__main__":
    root = tk.Tk()
    app = KabyleApp(root)
    root.mainloop()
