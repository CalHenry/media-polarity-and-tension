import json
from pathlib import Path

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

with open("data/test_feed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

sentences = [entry["title"] + ". " + entry["summary"] for entry in data["entries"]]

analyzer = SentimentIntensityAnalyzer()
for sentence in sentences:
    vs = analyzer.polarity_scores(sentence)
    # print(vs)
    print("{:-<65} {}".format(sentence, str(vs)))
