cout_total_formation = int(input("Cout total de la formation ?"))
dispo_cpf = int(input("Montant dispo CPF ?"))
revenu_mensuelle = int(input("Vos revenus mensuelle ?"))
depense_mensuelle = int(input("Vos dépenses mensuelles ?"))
duree_formation = int(input("Durée de la formation ?"))

reste_a_financer = cout_total_formation - dispo_cpf
epargne_dispo = (revenu_mensuelle - depense_mensuelle) * duree_formation
resultat_final = epargne_dispo - reste_a_financer

if resultat_final >= 0:
    print(f"--- ANALYSE SUR {duree_formation} MOIS EST VALIDE !---")
    print("Votre projet est financable entièrement")
    print(f" Il te restera {resultat_final} € une fois le diplome en poche")
else:
    print(f"Projet risqué sur {duree_formation} mois")
    print(f"Votre projet n'est pas financable entièrement, il manque {abs(resultat_final)}")
    print(f"Il te manque {abs(resultat_final)} € au total")

print("-" * duree_formation)

