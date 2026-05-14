import json

import spacy

# Load the French language model
nlp = spacy.load("fr_core_news_md")

# Define the article
article = """
Le ministre de l'Économie a accusé les syndicats de bloquer
les réformes nécessaires. Selon les manifestants, ces mesures
d'austérité aggravent les inégalités. Des affrontements ont
éclaté entre forces de l'ordre et protestataires à Lyon.
"""
article_2 = """
L’Etat hébreu poursuit ses frappes sur le Liban malgré la trêve, disant viser le Hezbollah pro-iranien.
Mardi, 13 personnes ont été tuées dans le sud du pays selon le ministère de la santé libanais, venant s’ajouter aux 380 morts depuis le début de la trêve, d’après la même source.
Jeudi, le Liban et Israël doivent tenir une nouvelle session de négociations, sous l’égide des Etats-Unis, à Washington.
"""

# Process the article with spaCy
doc = nlp(article_2)

spacy.displacy.serve(doc, style="dep")

with open("data/lexicons.json", "r") as f:
    lexicon = set(json.load(f))

# Count total tokens and lexicon matches
total_tokens = len(doc)
lexicon_matches = sum(1 for token in doc if token.text.lower() in lexicon)

# Calculate density (lexicon matches / total tokens)
density = lexicon_matches / total_tokens if total_tokens > 0 else 0.0

print(density)

"""
# Extract and print named entities
print("=== Named Entities ===")
for ent in doc.ents:
    print(f"{ent.text} ({ent.label_})")

# Extract and print noun phrases
print("\n=== Noun Phrases ===")
for chunk in doc.noun_chunks:
    print(chunk.text)

# Extract and print sentences
print("\n=== Sentences ===")
for sent in doc.sents:
    print(sent.text.strip())
"""
