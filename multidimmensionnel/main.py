from multidimmensionnel.extraction_insertion import *
from multidimmensionnel.connexion import Connexion


def main():
    Connexion.initConnexion()
    bdd = Connexion.get_bdd()

    if bdd:
        try:

            data = extraire_donnees_fichier('/Users/arsanabdi/PycharmProjects/SAE-S4-BD/relationnel/amazon-meta.txt')

            #  insertion_table_asin(bdd, data)        c'est parfait

            #  insertion_table_groupe(bdd, data)      c'est parfait

            #  insertion_table_client(bdd, data)

            #  insertion_table_produit(bdd, data)

            #  insertion_table_similaire(bdd, data)

            #  insertion_table_categorie_et_categorie_produit(bdd, data)

            #  insertion_table_review(bdd, data)

        except Exception as e:
            print(f"problème : {e}")
        finally:

            bdd.close()
            print("connexion fermée")
    else:
        print("connexion à la base de données impossible.")


if __name__ == "__main__":
    main()
