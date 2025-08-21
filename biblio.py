import random
import math
import time
from sentence_transformers import SentenceTransformer, util

def get_dict_champ_vide(niveau, verbe):

    personnes = ["1 si.", "2 si.", "3 si. m", "3 si. f", "1 pl.", "2 pl. m", "2 pl. f", "3 pl. m", "3 pl. f"]
    temps = ["Aoriste (impératif)", "Aoriste (futur)", "Prétérit", "Prétérit négatif"]

    colonnes = []
    for t in temps:
        for p in personnes:
            if t == "Aoriste (impératif)" and (p == "1 si." or p == "3 si. m" or p == "3 si. f" or p == "1 pl." or p == "3 pl. m" or p == "3 pl. f"):
                continue
            colonnes.append(f"{t}_{p}")
    colonnes = colonnes + ["part_aoriste", "part_pret_pos", "part_pret_neg"]

    print(colonnes)
    print(verbe)

    verbe_copy = verbe[3:]
    print(len(colonnes), len(verbe_copy))

    if niveau == "Avancé":
        nb_champs_vide = len(verbe_copy) - 1
    elif niveau == "Intermédiaire":
        nb_champs_vide = len(verbe_copy) - 5
    elif niveau == "Débutant":
        nb_champs_vide = 3 
        
    dict_reponse = {} # key: value dans colonne, value: reponse dans verbe
    for i, k in enumerate(colonnes):
        dict_reponse[k] = verbe_copy[i]
    
    
    indexs = random.sample(range(0, len(colonnes)-1), nb_champs_vide)
    print(indexs)
    
    champs_vides = [colonnes[i] for i in indexs]
    
    return dict_reponse, champs_vides

def jaccard_overlap(rep_joueur, bonne_reponse):
    set1 = set(rep_joueur.lower().split())
    set2 = set(bonne_reponse.lower().split())
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set2)

def score_semantique(reponse_joueur, bonne_reponse):
    from sentence_transformers import SentenceTransformer, util
    
    model = SentenceTransformer("all-mpnet-base-v2")
    emb1 = model.encode(reponse_joueur, convert_to_tensor=True)
    emb2 = model.encode(bonne_reponse, convert_to_tensor=True)
    sem_score = float(util.cos_sim(emb1, emb2))
    
    overlap = jaccard_overlap(reponse_joueur, bonne_reponse)

    # --- pondération dynamique ---
    # poids basé sur confiance sémantique
    conf_sem = min(max((sem_score - 0.4) / 0.6, 0), 1)  
    # poids basé sur recouvrement (on veut punir si très faible)
    conf_overlap = min(max((overlap - 0.2) / 0.8, 0), 1)

    # alpha augmente si sem_score est fiable, beta augmente si overlap est fiable
    alpha = 0.5 + 0.5 * conf_sem - 0.5 * (1 - conf_overlap)
    alpha = min(max(alpha, 0), 1)
    beta = 1 - alpha

    score = alpha * sem_score + beta * overlap
    print(f"sem={sem_score:.3f}, overlap={overlap:.3f}, alpha={alpha:.2f}, beta={beta:.2f}, final={score:.3f}")

    if score < 0.2:
        score = 0.0

    return min(round(score * 20, 2), 20)


"""rep_joueur = "le chien court"
a = time.time()
score = score_semantique(rep_joueur, "un chien est en train de courir")
b = time.time()
print(score, b - a)
s_sqrt = math.sqrt(score)
print(s_sqrt)
s_len_rep_joueur = math.sqrt(len(rep_joueur.split(" ")))
print(s_len_rep_joueur)"""
