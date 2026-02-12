# 🐍 Projet : Snake Game (POO)
> Objectif : Développer un moteur de jeu Snake en utilisant la Programmation Orientée Objet.

## 🛠️ Spécifications Logiques
* **Grille :** Système de coordonnées (X, Y).
* **Mouvement :** Translation de liste (Ajout Tête / Suppression Queue).
* **Règles :** - Le serpent meurt s'il touche les bords ou son propre corps.
    - Manger un fruit annule la suppression de la queue (croissance).

## 🧱 Architecture (Classes)
* **Classe Snake :** Gère la liste des positions, la direction et le mouvement.
* **Classe Food :** Gère la position aléatoire du fruit.
* **Classe Engine :** Chef d'orchestre qui gère la boucle de jeu et les collisions.