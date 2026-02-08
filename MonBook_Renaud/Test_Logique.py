# --- LA PORTE "ET" (AND) ---
# IL FAUT QUE LES DEUX SOIENT VRAIS POUR QUE LE RESULTAT SOIT VRAI

cle_contact = True
pied_sur_frein = True

demarrage = cle_contact and pied_sur_frein
print(f"La voiture démarre ? {demarrage}")

# --- LA PORTE "OU" (OR) ---
# Il suffit d'un seul Vrai pour que le résultat soit Vrai

carte_bleue = False
espece = True

achat_pain = carte_bleue or espece
print(f"Puis-je acheter du pain ? {achat_pain}")

# --- LA PORTE "NON" (NOT) ---
# Elle inverse le résultat

porte_ouverte = True
alarme_activee = not porte_ouverte
print(f"L'alarme est-elle activée ? {alarme_activee}")
