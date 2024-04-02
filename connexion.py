import psycopg2
from psycopg2 import OperationalError
import extraction_insertion


class Connexion:

    _bdd = None

    @staticmethod
    def initConnexion():

        host = 'database-etudiants.iut.univ-paris8.fr'
        database = 'aabdi'
        user = 'aabdi'
        password = 'LdUAAvjF'

        try:

            Connexion._bdd = psycopg2.connect(

                host=host, dbname=database, user=user, password=password
            )
            print('connexion réussie')

            data = extraction_insertion.extraire_donnees_fichier('amazon-meta.txt')
        except OperationalError:

            print(f'erreur')


# utilisation et test de la connexion
Connexion.initConnexion()
