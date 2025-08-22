import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import random

# Connexion SQLite
conn = sqlite3.connect("kabyle_learn.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS mots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    francais TEXT NOT NULL,
    kabyle TEXT NOT NULL,
    categorie_id INTEGER,
    FOREIGN KEY(categorie_id) REFERENCES categories(id)
)
""")
conn.commit()


class KabyleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Apprendre le Kabyle")
        self.root.geometry("1000x800") # Taille fixe

        self.screen_history = []  # historique des écrans
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)
        
        self.show_home()

        self.add_button = tk.Button(self.main_frame, text="Ajouter un mot", command=self.ajouter_mot, width=30, font=("Arial", 10))
        self.add_button.pack(pady=10)

        self.quiz_button = tk.Button(self.main_frame, text="Démarrer le challenge", command=self.lancer_quiz, width=30, font=("Arial", 10))
        self.quiz_button.pack(pady=10)

        self.view_button = tk.Button(self.main_frame, text="Visualiser la base", command=self.visualiser_base, width=30, font=("Arial", 10))
        self.view_button.pack(pady=10)

        self.categorie_button = tk.Button(self.main_frame, text="Catégories", command=self.gerer_categories, width=30, font=("Arial", 10))
        self.categorie_button.pack(pady=10)

    def change_screen(self, build_function, *args):
        # Sauvegarder l’écran actuel pour pouvoir revenir
        if hasattr(self, 'current_screen') and self.current_screen != build_function:
            self.screen_history.append((self.current_screen, self.current_args))

        # Vider l'écran
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Construire le nouvel écran
        self.current_screen = build_function
        self.current_args = args
        build_function(*args)
        
    def go_back(self):
        if self.screen_history:
            last_function, last_args = self.screen_history.pop()
            self.change_screen(last_function, *last_args)
    
    def show_home(self):
        tk.Label(self.main_frame, text="Accueil", font=("Arial", 16)).pack(pady=20)
        tk.Button(self.main_frame, text="Ajouter un mot", command=lambda: self.change_screen(self.ajouter_mot)).pack(pady=10)
        tk.Button(self.main_frame, text="Voir la base", command=lambda: self.change_screen(self.visualiser_base)).pack(pady=10)

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
        tk.Button(self.main_frame, text="← Retour", command=self.go_back).pack(pady=5)
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

        # Lignes
        for mot_id, fr, kab in mots:
            ligne = tk.Frame(frame_in_canvas)
            ligne.pack(anchor="w", pady=2)

            tk.Label(ligne, text=fr, width=30, font=("Arial", 10), anchor="w").grid(row=0, column=0, padx=5)
            tk.Label(ligne, text=kab, width=30, font=("Arial", 10), anchor="w").grid(row=0, column=1, padx=5)

            btn_supprimer = tk.Button(ligne, text="Supprimer", font=("Arial", 9),
                                    command=lambda mid=mot_id, win=view_window, cid=categorie_id: self.supprimer_mot(mid, win, cid))
            btn_supprimer.grid(row=0, column=2, padx=5)
            
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
        else:
            cursor.execute("SELECT francais, kabyle FROM mots")

        mots = cursor.fetchall()

        if len(mots) == 0:
            messagebox.showwarning("Aucun mot", "Ajoute des mots avant de démarrer le challenge.")
            return

        nb_questions = simpledialog.askinteger("Taille du quiz", "Combien de mots pour ce quiz ?", minvalue=1)

        if nb_questions is None:
            return

        total_mots = len(mots)
        if nb_questions >= total_mots:
            self.quiz_mots = mots
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

    def next_question(self):
        if self.current_index >= len(self.quiz_mots):
            self.fin_quiz()
            return

        mot_fr, mot_kab = self.quiz_mots[self.current_index]

        if random.choice([True, False]):
            self.question = mot_fr
            self.reponse_attendue = mot_kab
            self.label_question.config(text=f"Traduction en Kabyle de : {mot_fr}")
        else:
            self.question = mot_kab
            self.reponse_attendue = mot_fr
            self.label_question.config(text=f"Traduction en Français de : {mot_kab}")

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
            self.btn_next.config(text="Terminer", command=self.recap_window.destroy)
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




if __name__ == "__main__":
    root = tk.Tk()
    app = KabyleApp(root)
    root.mainloop()
