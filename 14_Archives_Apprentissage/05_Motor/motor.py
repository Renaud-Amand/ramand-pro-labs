# --- ÉTAPE 1 : LA BASE DE DONNÉES COMPLÈTE ---
alphabet = [
    ("A", "Avion"), ("B", "Ballon"), ("C", "Chat"), ("D", "Dauphin"),
    ("E", "Etoile"), ("F", "Fleur"), ("G", "Gourde"), ("H", "Hibou"),
    ("I", "Ile"), ("J", "Jardin"), ("K", "Kangourou"), ("L", "Lion"),
    ("M", "Maison"), ("N", "Nuage"), ("O", "Oiseau"), ("P", "Poisson"),
    ("Q", "Quille"), ("R", "Robot"), ("S", "Soleil"), ("T", "Tortue"),
    ("U", "Univers"), ("V", "Velo"), ("W", "Wagon"), ("X", "Xylophone"),
    ("Y", "Yaourt"), ("Z", "Zebre")
]

# --- ÉTAPE 2 : LE COMPTEUR ---
index = 0

# --- ÉTAPE 3 : LA BOUCLE DE JEU ---
for tour in range(26): # On teste sur 6 tours pour voir deux cycles complets
    
    # A. EXTRACTION (Dynamique grâce à l'index)
    lettre, objet = alphabet[index]
    
    # B. AFFICHAGE
    print(f"Lettre actuelle : {lettre} comme {objet}")

    # C. LOGIQUE DE PROGRESSION
    # On vérifie s'il reste des wagons après celui-ci
    if index < len(alphabet) - 1:
        index = index + 1  # ICI : on prend l'ancien index et on fait +1
    else:
        index = 0          # ICI : on est au bout, on repart à zéro

    print("--- Prochaine étape ---")