def extraire_donnees_fichier(fichier: str):
    produits = []

    with open(fichier, 'r') as fichier_avec_les_donnees:
        donnee_du_produit = []
        for ligne in fichier_avec_les_donnees:
            if ligne.startswith("Id:"):
                if donnee_du_produit:
                    produits.append(donnee_du_produit)
                    donnee_du_produit = []
            donnee_du_produit.append(ligne.strip())
        if donnee_du_produit:
            produits.append(donnee_du_produit)

    for produit in produits:
        del produit[-1]

    return produits


def insertion_table_asin(connexion, produits: list):
    cur = connexion.cursor()
    for produit in produits:

        if produit[0].startswith("Id:"):

            object_id = produit[0].split(":")[1].strip()
            asin = produit[1].split(":")[1].strip()

            cur.execute(
                'INSERT INTO bibliotheque.ASIN (idAsin, ASIN) VALUES (%s, %s) '
                'ON CONFLICT (idAsin) DO NOTHING;', (object_id, asin))
            connexion.commit()

        else:

            print("ce n'est pas un produit")

    cur.close()


def insertion_table_groupe(connexion, produits: list):
    cur = connexion.cursor()
    for produit in produits:

        if len(produit) > 3:

            nom_du_groupe = produit[3].split(":", 1)[1].strip()
            cur.execute('SELECT idGroupe FROM bibliotheque.GROUPE WHERE nom = %s;', (nom_du_groupe,))
            groupe_return_par_la_requete = cur.fetchone()
            if groupe_return_par_la_requete is None:

                cur.execute('INSERT INTO bibliotheque.GROUPE (nom) '
                            'VALUES (%s) RETURNING idGroupe;', (nom_du_groupe,))
                connexion.commit()
        else:
            print("pas de groupe pour le produit:", produit[0])

    cur.close()


def insertion_table_client(connexion, produits: list):
    cur = connexion.cursor()
    for produit in produits:
        if len(produit) > 3:

            debut_section_avis = next((i for i, item in enumerate(produit) if item.startswith("reviews: total:")), None)
            if debut_section_avis is not None and "downloaded: 0" not in produit[debut_section_avis]:

                tous_les_avis = produit[debut_section_avis + 1:]
                for un_avis_parmi_tous_les_avis in tous_les_avis:

                    if un_avis_parmi_tous_les_avis:

                        elements = un_avis_parmi_tous_les_avis.split()
                        if "cutomer:" in elements:

                            position_du_nom_client_dans_element = elements.index("cutomer:") + 1
                            nom_du_client = elements[position_du_nom_client_dans_element]
                            cur.execute(
                                'INSERT INTO bibliotheque.CLIENT (nom) VALUES '
                                '(%s) ON CONFLICT (nom) DO NOTHING;', (nom_du_client,))
                connexion.commit()
        else:
            print("pas d'infos sur le client:", produit[0])

    cur.close()


def insertion_table_produit(connexion, produits: list):
    print("Insertion")
    cur = connexion.cursor()

    for produit in produits:
        if len(produit) < 3 or 'discontinued product' in produit:

            print("Produit ignoré car discontinué")
            continue
        try:

            id_produit = int(produit[0].split(":")[1].strip())

            cur.execute('SELECT idProduit FROM bibliotheque.PRODUIT WHERE idProduit = %s;', (id_produit,))
            if cur.fetchone() is not None:
                continue

            print("gestion du produit", id_produit)
            num_asin = produit[1].split(":")[1].strip()
            titre = ": ".join(produit[2].split(": ")[1:]).strip() if len(produit) > 2 else 'Titre inconnu'
            nom_groupe = produit[3].split(":")[1].strip() if len(produit) > 3 else 'Groupe inconnu'
            salesrank = int(produit[4].split(":")[1].strip()) if len(produit) > 4 else 0
            nb_similar = int(produit[5].split(":")[1].strip().split()[0]) if len(produit) > 5 else 0
            nb_cat = int(produit[6].split(":")[1].strip()) if len(produit) > 6 else 0

            cur.execute('SELECT idGroupe FROM bibliotheque.GROUPE WHERE nom = %s;', (nom_groupe,))
            idGroupe = cur.fetchone()
            if idGroupe:

                idGroupe = idGroupe[0]
            else:

                print(f"groupe non trouvé pour id = ", id_produit)
                continue

            cur.execute('SELECT idAsin FROM bibliotheque.ASIN WHERE ASIN = %s;', (num_asin,))
            idAsin = cur.fetchone()
            if idAsin:

                idAsin = idAsin[0]
            else:

                print(f"asin non trouvé pour id = ", id_produit)
                continue

            total_review, download_review, avg_rate = extraire_informations_reviews(produit)

            cur.execute('''
            INSERT INTO bibliotheque.PRODUIT (idProduit, titre, salesrank, nb_similar,
            nb_cat, total_rev, dow_rev, avg_rate, idAsin, idGroupe) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (idProduit) DO UPDATE SET
            titre = EXCLUDED.titre, salesrank = EXCLUDED.salesrank, nb_similar = EXCLUDED.nb_similar, 
            nb_cat = EXCLUDED.nb_cat, total_rev = EXCLUDED.total_rev, dow_rev = EXCLUDED.dow_rev,
            avg_rate = EXCLUDED.avg_rate, idAsin = EXCLUDED.idAsin, idGroupe = EXCLUDED.idGroupe;
            ''', (id_produit, titre, salesrank, nb_similar, nb_cat, total_review, download_review, avg_rate, idAsin, idGroupe))
            connexion.commit()

        except Exception as e:
            print(f"erreur lors de l'insertion du produit", e)

    cur.close()


def extraire_informations_reviews(produit):
    for ligne in produit:

        if ligne.startswith("reviews:"):

            decoupage_de_la_ligne = ligne.split()
            try:

                position_total_review = decoupage_de_la_ligne.index("total:") + 1
                position_download_review = decoupage_de_la_ligne.index("downloaded:") + 1
                position_avg_rate = decoupage_de_la_ligne.index("avg") + 2

                total_review = int(decoupage_de_la_ligne[position_total_review])
                download_review = int(decoupage_de_la_ligne[position_download_review])
                avg_review = float(decoupage_de_la_ligne[position_avg_rate])

                return total_review, download_review, avg_review
            except (ValueError, IndexError):

                break

    return 0, 0, 0.0


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
                resultat_du_select = cur.fetchone()
                if resultat_du_select:

                    id_asin_similaire = resultat_du_select[0]
                    cur.execute('INSERT INTO bibliotheque.SIMILAIRE (idAsin, idAsinSimilaire) VALUES'
                                ' (%s, %s) ON CONFLICT DO NOTHING;', (object_id, id_asin_similaire))
                    connexion.commit()
                else:

                    cur.execute('SELECT idAsin FROM bibliotheque.ASIN ORDER BY idAsin DESC LIMIT 1;')
                    resultat = cur.fetchone()[0]

                    cur.execute('INSERT INTO bibliotheque.ASIN (idAsin, ASIN) VALUES'
                                ' (%s, %s) ON CONFLICT DO NOTHING;', (resultat + 1, number))
                    connexion.commit()

                    cur.execute('INSERT INTO bibliotheque.SIMILAIRE (idAsin, idAsinSimilaire) VALUES'
                                ' (%s, %s) ON CONFLICT DO NOTHING;', (object_id, resultat + 1))
                    connexion.commit()
        else:

            print("produit sans similaire: ", produit[0])

    cur.close()


def insertion_table_categorie_et_categorie_produit(connexion, produits: list):
    for produit in produits:

        if len(produit) < 4 or 'discontinued product' in produit or 'categories: 0' in produit:

            continue
        insertion_categories_et_association(connexion, produit)


def insertion_categories_et_association(connexion, produit):
    cur = connexion.cursor()
    object_id = int(produit[0].split(":")[1].strip())

    try:

        debut_section_categories = next((i for i, item in enumerate(produit) if "categories:" in item), None)
        debut_section_avis = next((i for i, item in enumerate(produit) if "reviews:" in item), None)
        if debut_section_categories is not None and debut_section_avis is not None:

            categories = produit[debut_section_categories + 1:debut_section_avis]
            id_parent_cat = None
            for ligne in categories:

                if 'cutomer:' in ligne:

                    break
                decoupage_en_categorie = ligne.split('|')
                for categorie in decoupage_en_categorie:

                    if not categorie.strip():

                        continue
                    nom_categorie, num_cat = categorie.strip().split('[')[:2]
                    num_cat = num_cat.split(']')[0]

                    if "cutomer:" not in nom_categorie:

                        cur.execute('''INSERT INTO bibliotheque.categorie (nom, num_cat, id_parent_cat)
                            VALUES (%s, %s, %s) ON CONFLICT (nom) DO UPDATE SET nom = EXCLUDED.nom
                            RETURNING idCat;''', (nom_categorie, int(num_cat), id_parent_cat))
                        result = cur.fetchone()
                        if result:

                            id_cat = result[0]
                            id_parent_cat = id_cat

                            cur.execute('''INSERT INTO bibliotheque.categorie_produit (idCat, idProduit)
                                VALUES (%s, %s) ON CONFLICT DO NOTHING;''', (id_cat, object_id))
                        else:

                            print(f"Aucun ID retourné pour la catégorie: ", nom_categorie)
                            continue
            connexion.commit()
    except Exception as e:

        print(f"erreur sur l'insertion des catégories : ", e)
    finally:

        cur.close()


def insertion_table_review(connexion, produits: list):
    cur = connexion.cursor()
    for produit in produits:

        if len(produit) > 3:

            try:

                id_du_produit = int(produit[0].split(":")[1].strip())
            except ValueError:

                print(f"ID de produit invalide: ", produit[0])
                continue

            debut_section_avis = next((i for i, item in enumerate(produit) if item.startswith("reviews:")), None)
            if debut_section_avis is not None:

                tous_les_avis = produit[debut_section_avis + 1:]
                for ligne in tous_les_avis:

                    if ligne:

                        decoupage_de_la_ligne = ligne.split()
                        if "cutomer:" in decoupage_de_la_ligne:

                            date = decoupage_de_la_ligne[0]
                            nom_du_client = decoupage_de_la_ligne[decoupage_de_la_ligne.index("cutomer:") + 1]
                            rating = int(decoupage_de_la_ligne[decoupage_de_la_ligne.index("rating:") + 1])
                            votes = int(decoupage_de_la_ligne[decoupage_de_la_ligne.index("votes:") + 1])
                            helpful = int(decoupage_de_la_ligne[decoupage_de_la_ligne.index("helpful:") + 1])

                            cur.execute('SELECT idClient FROM bibliotheque.CLIENT WHERE nom = %s;', (nom_du_client,))
                            resultat_de_la_requete = cur.fetchone()
                            if resultat_de_la_requete:

                                id_client_du_avis = resultat_de_la_requete[0]
                            else:

                                cur.execute('INSERT INTO bibliotheque.CLIENT (nom) VALUES (%s) '
                                            'RETURNING id_client_du_avis;', (nom_du_client,))
                                id_client_du_avis = cur.fetchone()[0] if cur.fetchone() else None
                                if id_client_du_avis is None:

                                    print(f"insertion du client impossible: ", nom_du_client)
                                    continue

                            try:

                                cur.execute(
                                    'INSERT INTO bibliotheque.REVIEW (idProduit, idClient, date, '
                                    'rating, votes, helpful) VALUES (%s, %s, %s, %s, %s, %s);',
                                    (id_du_produit, id_client_du_avis, date, rating, votes, helpful))
                            except Exception as e:

                                print(f"insertion de l'avis n'a pas marché: ", e)
                                connexion.rollback()
                                continue

                            connexion.commit()
    cur.close()






