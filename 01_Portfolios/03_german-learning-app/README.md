# Deutsch Profi — Allemand Professionnel Suisse

Clone Duolingo local pour apprendre l'allemand dans un contexte professionnel suisse.

## Cible

- **Chauffeurs poids lourds** : douane, véhicule, sécurité, route
- **Professionnels en entreprise** : entretien, réunion, administration
- Accent sur le **vocabulaire suisse** (vignette, Zoll, Grüezi...)

## Lancer l'app

```bash
pip install -r requirements.txt
python main.py
```

## Structure

```
main.py                    # Point d'entrée Kivy
screens/
  home_screen.py           # Accueil + liste des leçons
  lesson_screen.py         # Session d'apprentissage (type Duolingo)
database/
  progress_manager.py      # Suivi XP + progression locale
data/
  lessons.json             # Contenu des leçons (FR ↔ DE)
```

## Leçons Phase 1

| # | Leçon | Catégorie | Exercices |
|---|-------|-----------|-----------|
| 1 | 🚛 Véhicule Pro | Routier | 7 |
| 2 | 🛃 Douane & Documents | Routier | 7 |
| 3 | 💼 Entretien d'Embauche | Entreprise | 7 |
| 4 | 🤝 Réunion & Bureau | Entreprise | 6 |
| 5 | ⚠️ Sécurité Routière | Routier | 6 |

## Types d'exercices

- **Traduction FR → DE** : Saisir la traduction en allemand
- **Sélection (QCM)** : Choisir parmi 4 options

## Roadmap

- [ ] Phase 2 : Audio gTTS + 3 leçons supplémentaires
- [ ] Phase 2 : Supabase (sync cloud)
- [ ] Phase 2 : Stats avancées (streak, % maîtrise par catégorie)
- [ ] Phase 3 : Spécificités suisses renforcées
