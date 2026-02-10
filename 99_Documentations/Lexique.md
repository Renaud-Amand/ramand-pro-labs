#📖 `Lexique de Renaud`
---
- **Variable** : Comme une boîte étiquetée où on range une info (ex: `age = 33`).

- **String** : Du texte. Il faut toujours mettre des guillemets (ex: `"Bonjour"`).

- **Integer (int)** : Un nombre entier, sans guillemets (ex: `33`).

- **Floating Point (float)** : Un nombre décimal (ex: `33.5).

    - Exemple : (.2f) : Exemple n'afficher que 2 chiffres après la virgule.
    - Exemple : (.5f) : Exemple n'afficher que 5 chiffres après la virgule.

- **f-string** : (Formatted string) Une façon moderne d'intégrer des variables directement dans du texte en utilisant `f"Texte {variable}"`.
---
##🧠 `Mes premières fonctions`
---
- **print()** : La commande pour afficher quelque chose à l'écran.

- **input()** : Pour poser une question à l'utilisateur et récupérer sa réponse.

- **int()** : Transforme du texte en nombre ( avec la virgule) (ex: "33" devient 33).

- **str()** : Transforme un nombre en texte ( avec le + ) (ex: 34 devient "34").

- **`git add . ; git commit -m "Texte" ; git push`** : Push global sur GitHub.

- **Création** : On utilise des crochets `[]`.

    - Exemple : `ma_liste = ["A", "B", "C"]`

- **L'Index (La règle d'or)** : En informatique, on compte à partir de **0**.

    - `ma_liste[0]` est le 1er élément.
    - `ma_liste[1]` est le 2ème élément.

- **Ajouter** : `.append("élément")` ajoute à la fin de la liste.

- **Supprimer** : `.pop(index)` supprime l'élément à la position donnée et décale les autres.

- **Modifier** : `ma_liste[1]` = "Nouveau" remplace l'élément à l'index 1.

- **Mesurer** : `len(ma_liste)` donne le nombre total d'éléments.
---
###📋 `Les listes et fonctions de base`
---
- **Liste** : Une structure de données qui permet de stocker plusieurs éléments (nombres, chaînes de caractères, etc.) dans une seule variable, délimités par des crochets `[]`.

- **Index** : Le numéro de position d'un élément dans une liste. Attention : le premier élément est toujours à l'index **`0`**.

- **len()** : Fonction qui permet de compter le nombre d'éléments dans une liste (Length).

- **max() / min()** : Fonctions qui renvoient respectivement la valeur la plus haute et la plus basse d'une liste.

- **.append()** : Méthode qui permet d'ajouter un élément à la fin d'une liste.

- **.sort()** : Méthode qui trie les éléments d'une liste (par ordre croissant pour les nombres).

- **L'entrée utilisateur (`input`)** : Elle récupère toujours du texte (String).

- **La conversion (`float`)** : Indispensable pour trasnformer le texte en nombre et faire des calculs.

- **La priorité des calculs** : Toujours mettre des parenthèses pour les additions avant une divison `(a + b) / c`

- **Le f-string** : La méthode ultime pour afficher des variables proprement.
    - `f"Texte {ma_variable}"`
    - `{variable:.2f}` pour limiter les chiffres après la virgule
