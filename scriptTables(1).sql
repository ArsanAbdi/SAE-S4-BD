CREATE TABLE ASIN (
    idAsin INT PRIMARY KEY,
    ASIN VARCHAR(255)
);

CREATE TABLE GROUPE (
    idGroupe INT PRIMARY KEY,
    nom VARCHAR(50)
);

CREATE TABLE CLIENT (
    idClient INT PRIMARY KEY,
    nom VARCHAR(255)
);

CREATE TABLE PRODUIT (
    idProduit INT PRIMARY KEY,
    titre VARCHAR(255),
    salesrank INT,
    nb_similar INT,
    nb_cat INT,
    total_rev INT,
    dow_rev INT,
    avg_rate FLOAT,
    idGroupe INT,
    FOREIGN KEY (idGroupe) REFERENCES GROUPE(idGroupe)
);

CREATE TABLE CATEGORIE (
    idCat INT PRIMARY KEY,
    nom VARCHAR(100),
    num_cat INT,
    id_parent_cat INT,
    FOREIGN KEY (id_parent_cat) REFERENCES CATEGORIE(idCat)
);

CREATE TABLE REVIEW (
    idRev INT PRIMARY KEY,
    idProduit INT,
    idClient INT,
    date DATE,
    rating INT,
    votes INT,
    helpful INT,
    FOREIGN KEY (idProduit) REFERENCES PRODUIT(idProduit),
    FOREIGN KEY (idClient) REFERENCES CLIENT(idClient)
);

CREATE TABLE PRODUIT_ASIN (
    idProduit INT,
    idAsin INT,
    PRIMARY KEY (idProduit, idAsin),
    FOREIGN KEY (idProduit) REFERENCES PRODUIT(idProduit),
    FOREIGN KEY (idAsin) REFERENCES ASIN(idAsin)
);

CREATE TABLE CATEGORIE_PRODUIT (
    idProduit INT,    
    idCat INT,
    PRIMARY KEY (idCat, idProduit),
    FOREIGN KEY (idCat) REFERENCES CATEGORIE(idCat),
    FOREIGN KEY (idProduit) REFERENCES PRODUIT(idProduit)
);

CREATE TABLE SIMILAIRE (
    idAsin INT,
    idAsinSimilaire INT,
    PRIMARY KEY (idAsin, idAsinSimilaire),
    FOREIGN KEY (idAsin) REFERENCES ASIN(idAsin),
    FOREIGN KEY (idAsinSimilaire) REFERENCES ASIN(idAsin)
);

