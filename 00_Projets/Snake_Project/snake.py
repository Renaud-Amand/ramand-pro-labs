class Snake :
    def __init__(self):
        self.corps = [(100, 100), (90, 100), (80,100)]
        slef.direction = "DROITE"

    def avancer(selft):
        tete_actuelle = self.corps[-1]
        nouvelle_tete = (tete_actuelle[0] + 10, tete_actuelle[1])
        