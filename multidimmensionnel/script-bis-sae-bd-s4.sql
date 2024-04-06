DROP SCHEMA IF EXISTS bibliotheque_bis CASCADE;
CREATE SCHEMA bibliotheque_bis;
SET SEARCH_PATH TO bibliotheque_bis;

DROP TABLE IF EXISTS DATE_A, CLIENT, PRODUIT, CATEGORIE, REVIEW, SIMILAIRE,
					PRODUIT_ASIN, CATEGORIE_PRODUIT CASCADE;
CREATE TABLE CLIENT (
    idClient SERIAL PRIMARY KEY,
    nom VARCHAR(255)
);

CREATE TABLE DATE_A(
    idDate SERIAL PRIMARY KEY,
    jour    INT,
    mois    INT,
    annee   INT
);

CREATE TABLE PRODUIT (
    idProduit INT PRIMARY KEY,
    numAsin VARCHAR(10),
    groupe VARCHAR(30),
    titre VARCHAR(1000),
    salesrank INT,
    nb_similar INT,
    nb_cat INT,
    total_rev INT,
    dow_rev INT,
    avg_rate FLOAT
);

CREATE TABLE REVIEW (
    idRev SERIAL PRIMARY KEY,
    idProduit INT,
    idClient INT,
    idDate INT,
    rating INT,
    votes INT,
    helpful INT,
    FOREIGN KEY (idClient) REFERENCES CLIENT(idClient),
    FOREIGN KEY (idDate) REFERENCES DATE_A(idDate),
    FOREIGN KEY (idProduit) REFERENCES PRODUIT(idProduit)
);



CREATE TABLE CATEGORIE (
    idCat SERIAL PRIMARY KEY,
    nom VARCHAR(100),
    num_cat INT,
    id_parent_cat INT,
    FOREIGN KEY (id_parent_cat) REFERENCES CATEGORIE(idCat)
);

CREATE TABLE CATEGORIE_PRODUIT (
    idProduit INT,    
    idCat INT,
    PRIMARY KEY (idCat, idProduit),
    FOREIGN KEY (idCat) REFERENCES CATEGORIE(idCat),
    FOREIGN KEY (idProduit) REFERENCES PRODUIT(idProduit)
);


CREATE TABLE SIMILAIRE (
    idProduit INT,
    idProduitSimilaire INT,
    PRIMARY KEY (idProduit, idProduitSimilaire),
    FOREIGN KEY (idProduit) REFERENCES PRODUIT(idProduit),
    FOREIGN KEY (idProduitSimilaire) REFERENCES PRODUIT(idProduit)
);

ALTER TABLE bibliotheque_bis.CLIENT ADD CONSTRAINT client_nom_unique UNIQUE (nom);
ALTER TABLE bibliotheque_bis.CATEGORIE ADD CONSTRAINT categ_nom_unique UNIQUE (nom);
