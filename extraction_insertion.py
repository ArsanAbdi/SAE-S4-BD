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
    object_id = int(produit[0].split(":")[1].strip())  # pour le Id: 1
    asin = produit[1].split(":")[1].strip()  # ASIN: 0827229534

    cur = connexion.cursor()  # entrée en zone d'insertion

    # insertion table ASIN
    cur.execute('INSERT INTO bibliotheque.asin (idAsin, ASIN) VALUES (%s, %s) '
                'ON CONFLICT DO NOTHING;', (object_id, asin))

    #  pour le group ça se situe à la troisième ligne

    intitule_groupe = produit[3].split(":")[1].strip()  # group: Book

    #  on verifie si le groupe existe déjà
    cur.execute('SELECT idGroupe FROM bibliotheque.groupe WHERE nom = %s;', intitule_groupe)
    groupe = cur.fetchone()
    id_groupe = 0  # va nous servir plus tard
    if groupe:

        id_groupe = groupe[0]  # pour insérer ensuite le groupe dans produit
    else:

        cur.execute('INSERT INTO bibliotheque.groupe (idGroupe, nom) VALUES (%s, %s) RETURNING idGroupe;',
                    (object_id, intitule_groupe))
        id_groupe = cur.fetchone()[0]  # pour insérer ensuite dans la table produit

        connexion.commit()  # pour sauvegarder les changements


def inserer_donnees(connexion, produits):
    for produit in produits:

        if 'discontinued product' in produit['titre'].lower():

            continue
        else:

            traitement_insertion_produit(connexion, produit)
