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
                                'INSERT INTO bibliotheque_bis.CLIENT (nom) VALUES '
                                '(%s) ON CONFLICT (nom) DO NOTHING;', (nom_du_client,))
                connexion.commit()
        else:
            print("pas d'infos sur le client:", produit[0])

    cur.close()


def insertion_table_date(connexion, produits: list):
    cur = connexion.cursor()

    dates = {}

    for produit in produits:

        debut_section_avis = next((i for i, v in enumerate(produit) if v.startswith('reviews:')), None)

        if debut_section_avis is not None:
            avis = produit[debut_section_avis + 1:]

            for avis_ligne in avis:

                elements = avis_ligne.split()
                if "cutomer:" in elements:

                    date = elements[0]
                    date_elements = date.split('-')

                    annee = int(date_elements[0])
                    mois = int(date_elements[1])
                    jour = int(date_elements[2])

                    if date not in dates:
                        try:

                            cur.execute('''INSERT INTO bibliotheque_bis.DATE_A (jour, mois, annee)
                            VALUES (%s, %s, %s) RETURNING idDate;''', (jour, mois, annee))
                            id_date = cur.fetchone()[0]
                            connexion.commit()

                            dates[date] = id_date
                        except Exception as e:
                            print(f"erreur sur l'insert de la date: ", e)

    cur.close()


def insertion_table_produit(connexion, produits: list):
    cur = connexion.cursor()

    for produit in produits:
        if len(produit) < 3 or 'discontinued product' in produit:
            print("discontinué")
            continue

        try:
            id_produit = int(produit[0].split(":")[1].strip())
            asin = produit[1].split(":")[1].strip()
            groupe = produit[3].split(":")[1].strip() if len(produit) > 3 else 'Groupe inconnu'
            titre = ": ".join(produit[2].split(": ")[1:]).strip() if len(produit) > 2 else 'Titre inconnu'
            salesrank = int(produit[4].split(":")[1].strip()) if len(produit) > 4 else 0
            nb_similar = int(produit[5].split(":")[1].strip().split()[0]) if len(produit) > 5 else 0
            nb_cat = int(produit[6].split(":")[1].strip()) if len(produit) > 6 else 0

            total_review, download_review, avg_rate = extraire_informations_reviews(produit)

            cur.execute('''
            INSERT INTO bibliotheque_bis.PRODUIT (idProduit, numAsin, groupe, titre, salesrank, 
            nb_similar, nb_cat, total_rev, dow_rev, avg_rate) VALUES (%s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s) ON CONFLICT (idProduit) DO UPDATE SET titre = EXCLUDED.titre, 
            salesrank = EXCLUDED.salesrank, nb_similar = EXCLUDED.nb_similar, nb_cat = EXCLUDED.nb_cat, 
            total_rev = EXCLUDED.total_rev, dow_rev = EXCLUDED.dow_rev, avg_rate = EXCLUDED.avg_rate;
            ''', (id_produit, asin, groupe, titre, salesrank, nb_similar, nb_cat, total_review,
                  download_review, avg_rate))
            connexion.commit()

        except Exception as e:
            print(f"erreur sur l'insert du produit : ", e)

    cur.close()


def extraire_informations_reviews(produit):
    total_reviews, downloaded_reviews, avg_rating = 0, 0, 0.0

    debut_section_avis = next((i for i, v in enumerate(produit) if v.startswith('reviews:')), None)

    if debut_section_avis is not None:
        avis = produit[debut_section_avis]

        try:
            decoupage_du_avis = avis.split()
            total_reviews = decoupage_du_avis.index('total:') + 1
            downloaded_reviews = decoupage_du_avis.index('downloaded:') + 1
            avg_rating = decoupage_du_avis.index('avg') + 2

        except (ValueError, IndexError) as e:
            print(f"erreur extraction des données des avis : ", e)

    return total_reviews, downloaded_reviews, avg_rating


def insertion_table_review(connexion, produits: list):
    cur = connexion.cursor()

    for produit in produits:
        if "discontinued product" in produit or len(produit) < 4:
            continue

        id_produit = int(produit[0].split(":")[1].strip())

        debut_section_avis = next((i for i, item in enumerate(produit) if item.startswith("reviews:")), None)
        if debut_section_avis is not None:
            tous_les_avis = produit[debut_section_avis + 1:]
            for ligne in tous_les_avis:
                if "cutomer:" in ligne:
                    elements = ligne.split()
                    date_review = elements[0]
                    nom_client = elements[elements.index("cutomer:") + 1]
                    rating = int(elements[elements.index("rating:") + 1])
                    votes = int(elements[elements.index("votes:") + 1])
                    helpful = int(elements[elements.index("helpful:") + 1])

                    annee, mois, jour = map(int, date_review.split('-'))
                    date_format = f"{annee}-{mois:02d}-{jour:02d}"

                    cur.execute("SELECT idClient FROM bibliotheque_bis.CLIENT WHERE nom = %s;", (nom_client,))
                    id_client_result = cur.fetchone()
                    if not id_client_result:
                        cur.execute("INSERT INTO bibliotheque_bis.CLIENT (nom) VALUES (%s) RETURNING idClient;",
                                    (nom_client,))
                        id_client = cur.fetchone()[0]
                        connexion.commit()
                    else:
                        id_client = id_client_result[0]

                    cur.execute("SELECT idDate FROM bibliotheque_bis.DATE_A WHERE jour = %s AND mois = %s AND annee = %s;", (jour, mois, annee))
                    id_date_result = cur.fetchone()
                    if not id_date_result:
                        cur.execute("INSERT INTO bibliotheque_bis.DATE_A (jour, mois, annee) VALUES (%s, %s, %s) RETURNING idDate;", (jour, mois, annee))
                        id_date = cur.fetchone()[0]
                        connexion.commit()
                    else:
                        id_date = id_date_result[0]

                    try:
                        cur.execute("INSERT INTO bibliotheque_bis.REVIEW (idProduit, idClient, idDate, rating, votes, helpful) VALUES (%s, %s, %s, %s, %s, %s);",
                            (id_produit, id_client, id_date, rating, votes, helpful))
                        connexion.commit()
                    except Exception as e:
                        print(f"erreur insertion de l'avis: ", e)

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

                        cur.execute('''INSERT INTO bibliotheque_bis.CATEGORIE (nom, num_cat, id_parent_cat)
                            VALUES (%s, %s, %s) ON CONFLICT (nom) DO UPDATE SET nom = EXCLUDED.nom
                            RETURNING idCat;''', (nom_categorie, int(num_cat), id_parent_cat))
                        result = cur.fetchone()
                        if result:

                            id_cat = result[0]
                            id_parent_cat = id_cat

                            cur.execute('''INSERT INTO bibliotheque_bis.CATEGORIE_PRODUIT (idCat, idProduit)
                                VALUES (%s, %s) ON CONFLICT DO NOTHING;''', (id_cat, object_id))
                        else:

                            continue
            connexion.commit()
    except Exception as e:

        print(f"erreur sur l'insertion des catégories : ", e)
    finally:

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
                cur.execute('SELECT idProduit FROM bibliotheque_bis.PRODUIT WHERE numAsin = %s;', (number,))
                resultat_du_select = cur.fetchone()
                if resultat_du_select:

                    id_asin_similaire = resultat_du_select[0]
                    cur.execute('INSERT INTO bibliotheque_bis.SIMILAIRE (idProduit, idProduitSimilaire) VALUES'
                                ' (%s, %s) ON CONFLICT DO NOTHING;', (object_id, id_asin_similaire))
                    connexion.commit()
                else:
                    cur.execute('SELECT idProduit FROM bibliotheque_bis.PRODUIT ORDER BY idProduit DESC LIMIT 1;')
                    resultat = cur.fetchone()[0]

                    cur.execute('''
                    INSERT INTO bibliotheque_bis.PRODUIT (idProduit, numAsin, groupe, titre, salesrank, nb_similar, nb_cat, total_rev, dow_rev, avg_rate)
                    VALUES (%s, %s, 'Inconnu', 'Titre inconnu', 0, 0, 0, 0, 0, 0.0) ON CONFLICT DO NOTHING;
                    ''', (resultat + 1, number))
                    connexion.commit()

                    cur.execute('INSERT INTO bibliotheque_bis.SIMILAIRE (idProduit, idProduitSimilaire) VALUES'
                                ' (%s, %s) ON CONFLICT DO NOTHING;', (object_id, resultat + 1))
                    connexion.commit()
        else:

            print("produit sans similaire: ", produit[0])

    cur.close()






