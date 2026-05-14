import marimo

__generated_with = "0.23.6"
app = marimo.App(width="full")


@app.cell
def _():
    import json
    import numpy as np
    from bertopic import BERTopic
    from sentence_transformers import SentenceTransformer

    return BERTopic, SentenceTransformer, json


@app.cell
def _(json):
    with open("data/test_feed_data.json", "r", encoding="utf-8") as f:
        articles = json.load(f)
    return (articles,)


@app.cell
def _(articles):
    # Combine headline + summary for each article
    texts = [
        f"{article['title']}. {article['summary']}"
        for article in articles["entries"]
    ]
    return (texts,)


@app.cell
def _(SentenceTransformer, texts):
    # --- 2. Embed and fit BERTopic ---
    # Use a smaller model for prototyping (faster, less resource-intensive)
    embed_model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )  # Lightweight multilingual model
    embeddings = embed_model.encode(
        texts, show_progress_bar=True, convert_to_numpy=True
    )
    return (embeddings,)


@app.cell
def _(BERTopic):
    topic_model = BERTopic(
        language="français",
        calculate_probabilities=True,
        min_topic_size=2,
    )
    return (topic_model,)


@app.cell
def _(embeddings, texts, topic_model):
    topics, probabilities = topic_model.fit_transform(texts, embeddings)
    return probabilities, topics


@app.cell
def _(articles, probabilities, topics):
    # --- 3. Assign topic_id and topic_probability to each article ---
    for i, article in enumerate(articles):
        article["topic_id"] = int(topics[i])
        article["topic_probability"] = float(probabilities[i].max())
    return


@app.cell
def _(topic_model):
    # --- 5. Print topic info (optional) ---
    topic_info = topic_model.get_topic_info()
    print("\nTopic Overview:")
    print(topic_info)
    return


@app.cell
def _(articles, json):
    # --- 4. Save results ---
    with open("articles_with_topics.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)


    return


@app.cell
def _(BERTopic):
    from sklearn.datasets import fetch_20newsgroups

    # Create topics
    docs = fetch_20newsgroups(subset='all',  remove=('headers', 'footers', 'quotes'))['data']
    topic_model2 = BERTopic()
    topics2, probs2 = topic_model2.fit_transform(docs)
    return


@app.cell
def _(topic_model):
    similar_topics, similarity = topic_model.find_topics("motor", top_n=5)
    topic_model.get_topic(similar_topics[0])
    return


if __name__ == "__main__":
    app.run()
