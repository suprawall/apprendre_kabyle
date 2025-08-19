import random

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


    
    