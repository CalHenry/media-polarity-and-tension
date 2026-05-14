import json

import spacy

nlp = spacy.load("fr_core_news_md")


with open("data/test_feed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

"""
for entry in data["entries"]:
    text = entry["title"] + ". " + entry["summary"]
    doc = nlp(text)
    print(text)
    print([(w.text, w.pos_) for w in doc])
    print()
"""
article = """
Le ministre de l'Économie a accusé les syndicats de bloquer
les réformes nécessaires. Selon les manifestants, ces mesures
d'austérité aggravent les inégalités. Des affrontements ont
éclaté entre forces de l'ordre et protestataires à Lyon.
"""
doc = nlp(article)
# for token in doc:
#    print(token.text, token.pos_, token.dep_, token.lemma_)

non_punct_count = sum(1 for token in doc if not token.is_punct)
print("a")
print(non_punct_count)
