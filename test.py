string = [


'Id:   1',
'ASIN: 0827229534',
'title: Patterns of Preaching: A Sermon Sampler',
 'group: Book',
'salesrank: 396585',
'similar: 5  0804215715  156101074X  0687023955  0687074231  082721619X',
'categories: 2',
	'|Books[283155]|Subjects[1000]|Religion & Spirituality[22]|Christianity[12290]|Clergy[12360]|Preaching[12368]',
	'|Books[283155]|Subjects[1000]|Religion & Spirituality[22]|Christianity[12290]|Clergy[12360]|Sermons[12370]',
'reviews: total: 2  downloaded: 2  avg rating: 5',
	'2000-7-28  cutomer: A2JW67OY8U6HHK  rating: 5  votes:  10  helpful:   9',
	'2003-12-14  cutomer: A2VE83MZF98ITY  rating: 5  votes:   6  helpful:   5', ''




]

a = string[5].split(":")[1].strip()

print(a)

b = [a.split("  ")]

print(b)

def inserer_reviews(connexion, produit):
    cur = connexion.cursor()
    object_id = int(produit[0].split(":")[1].strip())

    try:
        # Trouver l'index où les reviews commencent
        index_reviews = next((i for i, item in enumerate(produit) if item.startswith("reviews: total:")), None)
        if index_reviews is not None:
            reviews = produit[
                      index_reviews + 1:]  # Toutes les lignes après "reviews: total:" sont considérées comme des reviews

            for review in reviews:
                if review:  # Vérifier que la ligne n'est pas vide
                    elements = review.split()
                    date_review = elements[0]
                    client_nom = elements[2]  # Supposer que le nom du client suit immédiatement 'cutomer:'
                    rating = int(elements[4])
                    votes = int(elements[6])
                    helpful = int(elements[8])

                    print(f"Insertion review pour le client : {client_nom}")

                    # Insérer le client s'il n'existe pas déjà
                    cur.execute(
                        'INSERT INTO bibliotheque.client (nom) VALUES (%s) ON CONFLICT (nom) DO NOTHING RETURNING idClient;',
                        (client_nom,))
                    id_client = cur.fetchone()
                    if id_client:
                        id_client = id_client[0]
                    else:
                        # Si le client existait déjà, récupérer son id
                        cur.execute('SELECT idClient FROM bibliotheque.client WHERE nom = %s;', (client_nom,))
                        id_client = cur.fetchone()[0]

                    print(f"Insertion avis : produit {object_id}, client {id_client}, date {date_review}")

                    # Insérer l'avis
                    cur.execute(
                        'INSERT INTO bibliotheque.review (idProduit, idClient, date, rating, votes, helpful) VALUES (%s, %s, %s, %s, %s, %s);',
                        (object_id, id_client, date_review, rating, votes, helpful))

            connexion.commit()

    except Exception as e:
        print(f"Erreur lors de l'insertion des reviews : {e}")
    finally:
        cur.close()


"""def traiter_nos_donnees(connexion, produits: list):
    cur = connexion.cursor()
    for produit in produits:
        if produit[0].startswith("Id:"):  # C'est un produit
            object_id = int(produit[0].split(":")[1].strip())
            asin = produit[1].split(":")[1].strip()
            titre = produit[2].split(":", 1)[1].strip()
            groupe_nom = produit[3].split(":", 1)[1].strip()

            # Recherche de l'idGroupe basé sur le nom du groupe
            cur.execute('SELECT idGroupe FROM bibliotheque.GROUPE WHERE nom = %s;', (groupe_nom,))
            groupe_result = cur.fetchone()
            if groupe_result:
                id_groupe = groupe_result[0]
            else:
                # Insertion du groupe s'il n'existe pas
                cur.execute('INSERT INTO bibliotheque.GROUPE (nom) VALUES (%s) RETURNING idGroupe;', (groupe_nom,))
                id_groupe = cur.fetchone()[0]
                connexion.commit()

            classement_vente = int(produit[4].split(":", 1)[1].strip())
            nb_similar = int(produit[5].split(":", 1)[1].split()[0].strip())

            # Extraction des données de revue
            total_rev, dow_rev, avg_rate = extraire_informations_reviews(produit)

            # Insertion ou mise à jour du produit
            cur.execute('''
                INSERT INTO bibliotheque.PRODUIT (idProduit, titre, salesrank, nb_similar, total_rev, dow_rev, avg_rate, idGroupe) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (idProduit) DO UPDATE SET 
                    titre = EXCLUDED.titre, salesrank = EXCLUDED.salesrank, nb_similar = EXCLUDED.nb_similar,
                    total_rev = EXCLUDED.total_rev, dow_rev = EXCLUDED.dow_rev, avg_rate = EXCLUDED.avg_rate, idGroupe = EXCLUDED.idGroupe;
            ''', (object_id, titre, classement_vente, nb_similar, total_rev, dow_rev, avg_rate, id_groupe))
            connexion.commit()

            # Insertion des catégories
            inserer_categories(connexion, produit, object_id)

            # Insertion des revues
            inserer_reviews(connexion, produit, object_id)

        else:
            print("Ce n'est pas un produit")

    cur.close()


# Fonction pour extraire les informations de revue
def extraire_informations_reviews(produit):
    for line in produit:
        if line.startswith("reviews:"):
            parts = line.split()
            total_rev_index = parts.index("total:") + 1
            dow_rev_index = parts.index("downloaded:") + 1
            avg_rate_index = parts.index("avg") + 2

            total_rev = int(parts[total_rev_index])
            dow_rev = int(parts[dow_rev_index])
            avg_rate = float(parts[avg_rate_index])

            return total_rev, dow_rev, avg_rate
    return 0, 0, 0.0

# Assumez que inserer_categories et inserer_reviews sont déjà définies"""