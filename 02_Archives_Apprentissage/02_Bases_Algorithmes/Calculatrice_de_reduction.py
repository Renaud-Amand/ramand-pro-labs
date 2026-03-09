prix = float(input(":Montant de ton panier ?"))

if prix >100:
    print("Remise de 20% appliquee !")
elif prix > 50:
    print("Remise de 10% appliquee !")
else:
    print("Pas de reduction !")
    