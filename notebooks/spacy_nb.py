import marimo

__generated_with = "0.23.6"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import spacy
    import json

    return json, spacy


@app.cell
def _(spacy):
    nlp = spacy.load("fr_core_news_md")
    return (nlp,)


@app.cell
def _(nlp):
    GOVT_LEXICON = {
        "gouvernement",
        "ministre",
        "président",
        "assemblée",
        "sénat",
        "préfecture",
        "mairie",
        "député",
        "commission",
        "police",
        "justice",
        "tribunal",
        "armée",
    }


    SUBJECT_DEPS = {
        "nsubj",
        "nsubj:pass",
    }


    def is_govt_subject(token, lexicon):

        lemma = token.lemma_.lower()

        if lemma in lexicon:
            return True

        # multi-token entities
        subtree_text = " ".join(t.text.lower() for t in token.subtree)

        for phrase in lexicon:
            if phrase in subtree_text:
                return True

        return False


    def govt_voice_ratio(text):

        doc = nlp(text)

        total_clauses = 0
        govt_clauses = 0

        for token in doc:
            # clause head
            if token.pos_ == "VERB":
                total_clauses += 1

                subjects = [
                    child for child in token.children if child.dep_ in SUBJECT_DEPS
                ]

                has_govt_subject = any(
                    is_govt_subject(subj, GOVT_LEXICON) for subj in subjects
                )

                if has_govt_subject:
                    govt_clauses += 1

        if total_clauses == 0:
            return 0.0

        return govt_clauses / total_clauses

    return (govt_voice_ratio,)


@app.cell
def _(json):
    with open("data/test_feed_data.json", "r") as f:
        articles = json.load(f)

    texts = [
        f"{article['title']}. {article['summary']}"
        for article in articles["entries"]
    ]
    return (texts,)


@app.cell
def _(govt_voice_ratio, texts):
    for sentence in texts:
        print("---")
        print(govt_voice_ratio(sentence))
    return


if __name__ == "__main__":
    app.run()
