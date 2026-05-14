import json

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# read data
with open("data/test_feed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

analyzer = SentimentIntensityAnalyzer()


def sentiment_fn(text: str) -> float:
    return analyzer.polarity_scores(text)["compound"]


def framing_gap(headline: str, body: str, sentiment_fn) -> float:
    headline_score = sentiment_fn(headline)
    body_score = sentiment_fn(body)
    return abs(headline_score - body_score)


for i, sentence in enumerate(data["entries"]):
    headline = sentence["title"]
    body = sentence["summary"]
    vs, headline_score, body_score = framing_gap(headline, body, sentiment_fn)
    print("---")
    print(headline_score)
    print(body_score)
    print(vs)
