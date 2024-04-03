import psycopg2
from psycopg2 import OperationalError


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
        except OperationalError as e:
            print(f'Erreur lors de la tentative de connexion : {e}')

    @staticmethod
    def get_bdd():
        return Connexion._bdd


# Utilisation et test de la connexion
Connexion.initConnexion()
