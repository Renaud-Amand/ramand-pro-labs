utilisateurs = ["Renaud", "Amélie", "Charlène"]
print("Voici ma liste", utilisateurs)
print("Le premier de ma liste est :", utilisateurs[0])
utilisateurs.append("Niky")
print("Après ajout", utilisateurs)
nombre = len(utilisateurs)
print("Il y a actuellement ", nombre, " utilisateurs")
utilisateurs.pop(1)
print("Après suppression de l'index 1", utilisateurs)
utilisateurs[1] = "Charlène-A"
print("Après modification de l'index 1", utilisateurs)