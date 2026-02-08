mdp = "33"
mdp_tape = input("Rentrez le mot de passe")
nom = input("Entrer votre nom")
age = int(input("Quel est votre âge ?"))
if nom == "Renaud" and age == 33 and mdp_tape == mdp:
    print("Accès autorisé")
else:
    print("Identité incorrect")
    print("Accès refusé, mais test publique autorisé")

experience_annees = int(input("Combiend d'années d'expérience avez-vous ?"))
print(f"Tu as {age} ans et tu as {experience_annees} ans d'expérience")

if age >= 33 and experience_annees >= 5:
    print("Profil Senior, Admission VAP prioritaire !")
elif age >= 30 :
    print("Profil standard, Admission classique")
else:
    print("Candidature non éligible")
