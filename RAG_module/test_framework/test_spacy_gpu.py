import spacy
from thinc.api import prefer_gpu

# Vérifier si le GPU est préféré
gpu_available = prefer_gpu()
print(f"GPU utilisé : {gpu_available}")

# Charger le modèle spaCy pour le français
nlp = spacy.load("fr_dep_news_trf")

# Traiter un texte exemple
doc = nlp("Ceci est un test pour vérifier l'utilisation du GPU.")

# Afficher l'analyse du texte
for token in doc:
    print(f"{token.text}: {token.pos_}, {token.dep_}")

print("Test terminé.")
