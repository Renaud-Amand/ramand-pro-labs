releves = [12.5, 9.2, 25.4, 20.0, 30.1]

nombre_mesure = len(releves)
plus_chaud = max(releves)
plus_froid = min(releves)

print(f"Analyse terminée sur {nombre_mesure} relevés")
print(f"La témperature la plus haute enregistrée est : {plus_chaud} °C")
print(f"La témperature la plus basse enregistrée est : {plus_froid} °C")

releves.sort()
print("relevés triés :", releves)