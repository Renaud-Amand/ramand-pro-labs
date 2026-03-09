objets = ["Potion", "codeball", "Super Bonbon", "Rappel", "Super Potion"]

for objet in objets:
    print(f"Vérification {objet}")
    if objet == "Super Bonbon":
        print("Super Bonbon trouvé ! arrêt de la recherche")
        break

niveaux_puissance = [35, 62, 48, 55, 73, 42, 68]

for niveau in niveaux_puissance:
    if niveau < 50:
        continue
    print(f"Niveau de puissance {niveau}")


print("---" * 3)

