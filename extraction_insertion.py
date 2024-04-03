




import psycopg2

def extraire_donnees_fichier(fichier: str):
    livres = []

    with open(fichier, 'r') as fichier_data:
        donnee_livre = []
        for line in fichier_data:
            if line.startswith("Id:"):
                if donnee_livre:
                    livres.append(donnee_livre)
                    donnee_livre = []
            donnee_livre.append(line.strip())
        if donnee_livre:
            livres.append(donnee_livre)

    return livres


def traitement_insertion_produit(connexion, produit):
    cur = connexion.cursor()

    with open('script-sae-bd-s4.sql', 'r') as fichier:
        script = fichier.read()
        commandes = script.split(';')  # Sépare le script en commandes individuelles
        for commande in commandes:
            if commande.strip():
                cur.execute(commande)

    connexion.commit()

    # Extrait l'ID, ASIN, et titre du produit
    object_id = int(produit[0].split(":")[1].strip())
    asin = produit[1].split(":")[1].strip()
    titre = produit[2].split(":")[1].strip()
    groupe = produit[3].split(":")[1].strip()
    salesrank = int(produit[4].split(":")[1].strip())

    # Insertion dans la table ASIN si pas déjà présent
    cur.execute('INSERT INTO ASIN (idAsin, ASIN) VALUES (%s, %s) ON CONFLICT DO NOTHING;',
                (object_id, asin))

    # Gestion du groupe
    cur.execute('SELECT idGroupe FROM bibliotheque.groupe WHERE nom = %s;', (groupe,))
    groupe_result = cur.fetchone()
    if groupe_result:
        id_groupe = groupe_result[0]
    else:
        cur.execute('INSERT INTO bibliotheque.groupe (nom) VALUES (%s) RETURNING idGroupe;', (groupe,))
        id_groupe = cur.fetchone()[0]

    # Insertion du produit
    cur.execute(
        'INSERT INTO bibliotheque.produit (idProduit, titre, salesrank, idGroupe) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;',
        (object_id, titre, salesrank, id_groupe)
    )

    # Insertion des catégories
    categories = [c for c in produit if c.startswith('|')]
    for categorie in categories:
        nom_categorie = categorie.split('|')[-1]
        cur.execute(
            'INSERT INTO bibliotheque.categorie (nom) VALUES (%s) ON CONFLICT (nom) DO NOTHING RETURNING idCat;',
            (nom_categorie,))
        id_cat = cur.fetchone()[0]
        cur.execute(
            'INSERT INTO bibliotheque.categorie_produit (idCat, idProduit) VALUES (%s, %s) ON CONFLICT DO NOTHING;',
            (id_cat, object_id))

    # Insertion des reviews
    reviews = [r for r in produit if
               r.count('-') == 2]  # Une façon simple d'identifier les lignes contenant des dates de reviews
    for review in reviews:
        date, client, rating, votes, helpful = extract_review_data(review)
        # Ici, vous devriez ajouter une logique pour insérer les reviews.
        # Assurez-vous d'extraire et d'utiliser le idClient pour le champ idClient.

    connexion.commit()
    cur.close()


def extract_review_data(review):
    # Vous devez définir cette fonction pour extraire correctement les données d'une review à partir de la chaîne de caractères.
    # Exemple simple :
    parts = review.split()
    date = parts[0]
    client = parts[3]  # Suppose que le client est toujours au 4e élément; ajustez selon le format réel
    rating = int(parts[6])  # Ajustez les indices selon le format réel
    votes = int(parts[8])  # Ajustez
    helpful = int(parts[10])  # Ajustez
    return date, client, rating, votes, helpful

