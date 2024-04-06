DROP SCHEMA IF EXISTS bibliotheque CASCADE;
CREATE SCHEMA bibliotheque;

DROP TABLE IF EXISTS bibliotheque.ASIN, bibliotheque.GROUPE, bibliotheque.CLIENT,
					bibliotheque.PRODUIT, bibliotheque.CATEGORIE, bibliotheque.REVIEW, 
					bibliotheque.PRODUIT_ASIN, bibliotheque.CATEGORIE_PRODUIT CASCADE;

CREATE TABLE bibliotheque.ASIN (
    idAsin INT PRIMARY KEY,
    ASIN VARCHAR(10) 
);

CREATE TABLE bibliotheque.GROUPE (
    idGroupe SERIAL PRIMARY KEY,
    nom VARCHAR(50)
);

CREATE TABLE bibliotheque.CLIENT (
    idClient SERIAL PRIMARY KEY,
    nom VARCHAR(255) UNIQUE
);

CREATE TABLE bibliotheque.CATEGORIE (
    idCat SERIAL PRIMARY KEY,
    nom VARCHAR(100),
    num_cat INT,
    id_parent_cat INT,
    FOREIGN KEY (id_parent_cat) REFERENCES bibliotheque.CATEGORIE(idCat)
);

CREATE TABLE bibliotheque.PRODUIT (
    idProduit INT PRIMARY KEY,
    titre VARCHAR(1000),
    salesrank INT,
    nb_similar INT,
    nb_cat INT,
    total_rev INT,
    dow_rev INT,
    avg_rate FLOAT,
    idGroupe INT,
    idAsin INT,
    FOREIGN KEY (idAsin) REFERENCES bibliotheque.ASIN(idAsin),
    FOREIGN KEY (idGroupe) REFERENCES bibliotheque.GROUPE(idGroupe)
);

CREATE TABLE bibliotheque.SIMILAIRE (
    idAsin INT,
    idAsinSimilaire INT,
    PRIMARY KEY (idAsin, idAsinSimilaire),
    FOREIGN KEY (idAsin) REFERENCES bibliotheque.ASIN(idAsin),
    FOREIGN KEY (idAsinSimilaire) REFERENCES bibliotheque.ASIN(idAsin)
);



CREATE TABLE bibliotheque.CATEGORIE_PRODUIT (
    idCat INT,
    idProduit INT,
    PRIMARY KEY (idCat, idProduit),
    FOREIGN KEY (idCat) REFERENCES bibliotheque.CATEGORIE(idCat),
    FOREIGN KEY (idProduit) REFERENCES bibliotheque.PRODUIT(idProduit)
);

CREATE TABLE bibliotheque.REVIEW (
    idRev SERIAL PRIMARY KEY,
    idProduit INT,
    idClient INT,
    date DATE,
    rating INT,
    votes INT,
    helpful INT,
    FOREIGN KEY (idProduit) REFERENCES bibliotheque.PRODUIT(idProduit),
    FOREIGN KEY (idClient) REFERENCES bibliotheque.CLIENT(idClient)
);

ALTER TABLE bibliotheque.CATEGORIE ADD CONSTRAINT categ_nom_unique UNIQUE (nom);

