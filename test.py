from relationnel.extraction_insertion import extraire_donnees_fichier


ddonnee = extraire_donnees_fichier('amazon-meta.txt')

vrai = []
for a in ddonnee:

    if 'discontinued product' in a:
        vrai.append(a)

print(len(vrai))