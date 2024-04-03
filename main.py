from extraction_insertion import extraire_donnees_fichier, traitement_insertion_produit
from connexion import Connexion  # Assurez-vous que le chemin d'importation est correct


def main():
    Connexion.initConnexion()
    bdd = Connexion.get_bdd()
    if bdd:
        try:
            data = extraire_donnees_fichier('amazon-meta.txt')
            for produit in data:
                traitement_insertion_produit(bdd, produit)
        except Exception as e:
            print(f"Une erreur est survenue lors de l'extraction ou de l'insertion: {e}")
        finally:
            bdd.close()
    else:
        print("Impossible d'établir une connexion à la base de données.")


if __name__ == "__main__":
    main()