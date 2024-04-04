def extraire_donnees_fichier(fichier: str):
    produits = []

    with open(fichier, 'r') as fichier_data:
        donnee_produit = []
        for line in fichier_data:
            if line.startswith("Id:"):
                if donnee_produit:
                    produits.append(donnee_produit)
                    donnee_produit = []
            donnee_produit.append(line.strip())
        if donnee_produit:
            produits.append(donnee_produit)

    for produit in produits:
        del produit[-1]

    return produits


def insertion_table_asin(connexion, produits: list):
    cur = connexion.cursor()
    for produit in produits:

        if produit[0].startswith("Id:"):  # c'est un produit

            object_id = produit[0].split(":")[1].strip()
            asin = produit[1].split(":")[1].strip()

            cur.execute(
                'INSERT INTO bibliotheque.ASIN (idAsin, ASIN) VALUES (%s, %s) ON CONFLICT (idAsin) DO NOTHING;',
                (object_id, asin))

            connexion.commit()

        else:  # ce n'est pas un produit

            print("ce n'est pas un produit")

    cur.close()


def insertion_table_groupe(connexion, produits: list):
    cur = connexion.cursor()
    for produit in produits:
        if len(produit) > 3:
            groupe_nom = produit[3].split(":", 1)[1].strip()
            cur.execute('SELECT idGroupe FROM bibliotheque.GROUPE WHERE nom = %s;', (groupe_nom,))
            groupe_result = cur.fetchone()
            if groupe_result is None:
                cur.execute('INSERT INTO bibliotheque.GROUPE (nom) VALUES (%s) RETURNING idGroupe;', (groupe_nom,))
                connexion.commit()
        else:
            print("Produit sans information de groupe:", produit[0])

    cur.close()


def insertion_table_client(connexion, produits: list):
    cur = connexion.cursor()
    for produit in produits:
        if len(produit) > 3:

            index_reviews = next((i for i, item in enumerate(produit) if item.startswith("reviews: total:")), None)

            if index_reviews is not None and "downloaded: 0" not in produit[index_reviews]:

                reviews = produit[index_reviews + 1:]
                for review in reviews:
                    if review:

                        elements = review.split()
                        if "cutomer:" in elements:
                            client_index = elements.index("cutomer:") + 1
                            client_nom = elements[client_index]

                            cur.execute(
                                'INSERT INTO bibliotheque.CLIENT (nom) VALUES (%s) ON CONFLICT (nom) DO NOTHING;',
                                (client_nom,)
                            )
                connexion.commit()
        else:
            print("Produit sans information de client:", produit[0])

    cur.close()


def extraire_informations_reviews(produit):
    """
    Extrait les informations relatives aux reviews d'un produit.

    Paramètres:
    - produit: list, une liste de chaînes de caractères contenant les informations d'un produit.

    Retourne:
    - total_rev: int, le nombre total de reviews.
    - dow_rev: int, le nombre de reviews téléchargées.
    - avg_rate: float, la note moyenne des reviews.
    """
    for line in produit:
        if line.startswith("reviews:"):
            parts = line.split()
            try:
                total_rev_index = parts.index("total:") + 1
                dow_rev_index = parts.index("downloaded:") + 1
                avg_rate_index = parts.index("avg") + 2

                total_rev = int(parts[total_rev_index])
                dow_rev = int(parts[dow_rev_index])
                avg_rate = float(parts[avg_rate_index])

                return total_rev, dow_rev, avg_rate
            except (ValueError, IndexError):
                # En cas d'erreur lors de l'extraction des données, retourner des valeurs par défaut.
                break

    # Retourner des valeurs par défaut si les informations de review ne sont pas trouvées ou en cas d'erreur.
    return 0, 0, 0.0


def insertion_table_produit(connexion, produits: list):
    cur = connexion.cursor()

    for produit in produits:
        if len(produit) < 3 or 'discontinued product' in produit:
            # Ignore les produits discontinués ou ceux avec des informations manquantes
            continue

        try:
            id_produit = int(produit[0].split(":")[1].strip())
            ASIN_text = produit[1].split(":")[1].strip()
            titre = ": ".join(produit[2].split(": ")[1:]).strip() if len(produit) > 2 else 'Titre inconnu'
            groupe_nom = produit[3].split(":")[1].strip() if len(produit) > 3 else 'Groupe inconnu'
            salesrank = int(produit[4].split(":")[1].strip()) if len(produit) > 4 else 0
            nb_similar = int(produit[5].split(":")[1].strip().split()[0]) if len(produit) > 5 else 0
            nb_cat = int(produit[6].split(":")[1].strip()) if len(produit) > 6 else 0

            # Trouver l'idGroupe correspondant au groupe_nom
            cur.execute('SELECT idGroupe FROM bibliotheque.GROUPE WHERE nom = %s;', (groupe_nom,))
            idGroupe = cur.fetchone()
            if idGroupe:
                idGroupe = idGroupe[0]
            else:
                print(f"Groupe non trouvé pour le produit {id_produit}")
                continue

            # Trouver l'idAsin correspondant à ASIN
            cur.execute('SELECT idAsin FROM bibliotheque.ASIN WHERE ASIN = %s;', (ASIN_text,))
            idAsin = cur.fetchone()
            if idAsin:
                idAsin = idAsin[0]
            else:
                print(f"ASIN non trouvé pour le produit {id_produit}")
                continue

            # Extraire les informations de reviews
            total_rev, dow_rev, avg_rate = extraire_informations_reviews(produit)

            # Insertion dans la table PRODUIT
            cur.execute('''
            INSERT INTO bibliotheque.PRODUIT 
            (id_produit, titre, salesrank, nb_similar, nb_cat, total_rev, dow_rev, avg_rate, idAsin, idGroupe) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id_produit) DO UPDATE SET
            titre = EXCLUDED.titre,
            salesrank = EXCLUDED.salesrank,
            nb_similar = EXCLUDED.nb_similar,
            nb_cat = EXCLUDED.nb_cat,
            total_rev = EXCLUDED.total_rev,
            dow_rev = EXCLUDED.dow_rev,
            avg_rate = EXCLUDED.avg_rate,
            idAsin = EXCLUDED.idAsin,
            idGroupe = EXCLUDED.idGroupe;
            ''', (id_produit, titre, salesrank, nb_similar, nb_cat, total_rev, dow_rev, avg_rate, idAsin, idGroupe))

            connexion.commit()

        except Exception as e:
            print(f"Erreur lors de l'insertion du produit {id_produit} : {e}")

    cur.close()


def insertion_table_similaire(connexion, produits: list):
    cur = connexion.cursor()
    for produit in produits:

        if len(produit) > 3:
            object_id = produit[0].split(":")[1].strip()
            ligne_similar = produit[5].split(":")[1].strip()
            decoupage_ligne_similar = ligne_similar.split()
            del (decoupage_ligne_similar[0])

            for number in decoupage_ligne_similar:
                cur.execute('SELECT idAsin FROM bibliotheque.ASIN WHERE ASIN = %s;', (number,))
                result = cur.fetchone()
                if result:  # S'assurer qu'un ASIN correspondant a été trouvé
                    id_asin_similaire = result[0]
                    cur.execute('INSERT INTO bibliotheque.SIMILAIRE (idAsin, idAsinSimilaire) VALUES (%s, %s);',
                                (object_id, id_asin_similaire))
                    connexion.commit()
        else:

            print("Produit sans information de similarité:", produit[0])

    cur.close()


def insertion_table_categorie_et_categorie_produit(connexion, produits: list):
    for produit in produits:
        # Vérifier si le produit est discontinué ou s'il n'a pas de catégories
        if len(produit) < 4 or 'discontinued product' in produit or 'categories: 0' in produit:
            continue

        # Utilisation de la fonction renommée pour l'insertion des catégories et de l'association
        insertion_categories_et_association(connexion, produit)


def insertion_categories_et_association(connexion, produit):
    cur = connexion.cursor()
    object_id = int(produit[0].split(":")[1].strip())

    try:
        # Trouver les indices de début et de fin pour les catégories
        index_categories = next((i for i, item in enumerate(produit) if "categories:" in item), None)
        index_reviews = next((i for i, item in enumerate(produit) if "reviews:" in item), None)

        if index_categories is not None and index_reviews is not None:
            categories = produit[index_categories + 1:index_reviews]
            id_parent_cat = None
            for categorie_line in categories:
                if 'cutomer:' in categorie_line:  # Indique le début des reviews
                    break  # Arrête le traitement des catégories ici
                categorie_path = categorie_line.split('|')
                for categorie in categorie_path:
                    if not categorie.strip():  # Ignore les chaînes vides
                        continue
                    nom_categorie, num_cat = categorie.strip().split('[')[:2]
                    num_cat = num_cat.split(']')[0]

                    # Assurez-vous que les données de catégorie ne sont pas des reviews
                    if "cutomer:" not in nom_categorie:
                        cur.execute(
                            '''
                            INSERT INTO bibliotheque.categorie (nom, num_cat, id_parent_cat)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (nom) DO UPDATE SET nom = EXCLUDED.nom RETURNING idCat;
                            ''',
                            (nom_categorie, int(num_cat), id_parent_cat)
                        )
                        result = cur.fetchone()
                        if result:
                            id_cat = result[0]
                            id_parent_cat = id_cat  # Mise à jour pour la prochaine itération

                            # Insertion dans categorie_produit
                            cur.execute(
                                '''
                                INSERT INTO bibliotheque.categorie_produit (idCat, idProduit)
                                VALUES (%s, %s) ON CONFLICT DO NOTHING;
                                ''',
                                (id_cat, object_id)
                            )
                        else:
                            print(f"Aucun ID retourné pour la catégorie: {nom_categorie}")
                            continue
            connexion.commit()
    except Exception as e:
        print(f"Erreur lors de l'insertion des catégories pour le produit {object_id} : {e}")
    finally:
        cur.close()


def insertion_table_review(connexion, produits: list):
    cur = connexion.cursor()

    for produit in produits:
        if len(produit) > 3:
            # On essaye de convertir l'ID du produit en entier, on ignore le produit s'il y a une erreur
            try:
                idProduit = int(produit[0].split(":")[1].strip())
            except ValueError:
                print(f"ID de produit invalide: {produit[0]}")
                continue

            # On extrait l'indice de début des reviews
            index_reviews = next((i for i, item in enumerate(produit) if item.startswith("reviews:")), None)
            if index_reviews is not None:
                reviews_data = produit[index_reviews + 1:]

                for review_line in reviews_data:
                    if review_line:
                        elements = review_line.split()
                        if "cutomer:" in elements:
                            customer_name = elements[elements.index("cutomer:") + 1]
                            rating = int(elements[elements.index("rating:") + 1])
                            votes = int(elements[elements.index("votes:") + 1])
                            helpful = int(elements[elements.index("helpful:") + 1])
                            date_review = elements[0]

                            # On vérifie si le client existe déjà et on récupère son id, sinon on l'insère
                            cur.execute('SELECT idClient FROM bibliotheque.CLIENT WHERE nom = %s;', (customer_name,))
                            result = cur.fetchone()
                            if result:
                                idClient = result[0]
                            else:
                                # Insérer le client s'il n'existe pas déjà et récupérer son id
                                cur.execute('INSERT INTO bibliotheque.CLIENT (nom) VALUES (%s) RETURNING idClient;',
                                            (customer_name,))
                                idClient = cur.fetchone()[0] if cur.fetchone() else None
                                if idClient is None:
                                    print(f"Impossible d'insérer ou de récupérer le client: {customer_name}")
                                    continue

                            # Maintenant on peut insérer la review
                            try:
                                cur.execute(
                                    'INSERT INTO bibliotheque.REVIEW (idProduit, idClient, date, rating, votes, helpful) VALUES (%s, %s, %s, %s, %s, %s);',
                                    (idProduit, idClient, date_review, rating, votes, helpful)
                                )
                            except Exception as e:
                                print(f"Erreur lors de l'insertion de la review: {e}")
                                connexion.rollback()
                                continue

                            # On valide l'insertion
                            connexion.commit()

    cur.close()


def parse_review_line(line):
    """
    Parse une ligne de review et extrait les informations nécessaires.
    """
    elements = line.split()
    date_review = elements[0]
    customer_index = elements.index('cutomer:') + 1
    customer = elements[customer_index]
    rating = int(elements[customer_index + 2])
    votes = int(elements[customer_index + 4])
    helpful = int(elements[customer_index + 6])
    return date_review, customer, rating, votes, helpful
