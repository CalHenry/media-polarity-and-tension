import json

import feedparser

# feed = feedparser.parse("https://www.lemonde.fr/rss/une.xml")
feed = feedparser.parse("https://www.lemonde.fr/politique/rss_full.xml")

feed_dict = {
    "feed_title": feed.feed.get("title", ""),
    "feed_link": feed.feed.get("link", ""),
    "entries": [
        {
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
            "summary": entry.get("summary", ""),
        }
        for entry in feed.entries
    ],
}
for e in feed.entries:
    print(f"title:      {e.get('title')}")


with open("data/feed_data_pol.json", "w", encoding="utf-8") as json_file:
    json.dump(feed_dict, json_file, ensure_ascii=False)
