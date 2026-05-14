import json

from transformers import pipeline

# data
with open("data/feed_data_pol.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# transformers
classifier = pipeline(
    task="text-classification",
    # task="sentiment-analysis",
    model="cmarkea/distilcamembert-base-sentiment",
    tokenizer="cmarkea/distilcamembert-base-sentiment",
    return_all_scores=True,
)


for i, sentence in enumerate(data["entries"]):
    headline = sentence["title"]
    body = sentence["summary"]
    print("---")
    headline_score = classifier(headline)
    body_score = classifier(body)

    # Mapping for star ratings to sentiment labels
    star_to_sentiment = {
        "1 star": "very negative",
        "2 stars": "negative",
        "3 stars": "neutral",
        "4 stars": "positive",
        "5 stars": "very positive",
    }

    # Extract and convert scores
    headline_label = headline_score[0]["label"]
    headline_sentiment = star_to_sentiment.get(headline_label, headline_label)

    body_label = body_score[0]["label"]
    body_sentiment = star_to_sentiment.get(body_label, body_label)

    print(headline)
    print(f"hd_score = {headline_sentiment} (original: {headline_label})")
    print(f"body_score = {body_sentiment} (original: {body_label})")
