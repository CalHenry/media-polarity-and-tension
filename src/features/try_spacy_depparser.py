import json

import spacy

nlp = spacy.load("fr_core_news_md")


def passive_voice_ratio(text):
    doc = nlp(text)

    total_verbs = 0
    passive_verbs = 0

    for token in doc:
        # count lexical verbs
        if token.pos_ == "VERB":
            total_verbs += 1

            morph = token.morph

            is_participle = "VerbForm=Part" in morph

            if is_participle:
                # search auxiliaries
                aux_children = [
                    child
                    for child in token.children
                    if child.dep_ in {"aux", "aux:pass"}
                ]

                has_etre_aux = any(aux.lemma_ == "être" for aux in aux_children)

                # stronger signal:
                has_par_agent = any(
                    child.text.lower() == "par" for child in token.children
                )

                if has_etre_aux and (has_par_agent or True):
                    passive_verbs += 1

    if total_verbs == 0:
        return 0.0

    return passive_verbs / total_verbs


text = """
Le projet a été approuvé par le gouvernement.
Les manifestants dénoncent la réforme.
La décision a été prise rapidement.
"""

with open("data/test_feed_data.json", "r") as f:
    articles = json.load(f)


texts = [f"{article['title']}. {article['summary']}" for article in articles["entries"]]

for sentence in texts:
    print("---")
    print(passive_voice_ratio(sentence))
