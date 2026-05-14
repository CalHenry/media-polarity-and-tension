import json

import numpy as np
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer

vectorizer_model = CountVectorizer(stop_words="français")

with open("data/test_feed_data.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

texts = [f"{article['title']}. {article['summary']}" for article in articles["entries"]]

embed_model = SentenceTransformer("all-MiniLM-L6-v2")  # Lightweight multilingual model
embeddings = embed_model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

topic_model = BERTopic(
    language="français",
    calculate_probabilities=True,
    min_topic_size=2,
)

topic, probabilities = topic_model.fit_transform(texts, embeddings)

print(topic_model.get_topic_info())
print("---")
print(topic_model.get_document_info(texts))
