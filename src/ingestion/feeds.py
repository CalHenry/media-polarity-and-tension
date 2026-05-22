from datetime import datetime, timezone
from pathlib import Path

import feedparser
import polars as pl

OUTLETS = [
    (
        "Le Monde",
        "center / liberal establishment",
        "https://www.lemonde.fr/rss/une.xml",
    ),
    (
        "Le Figaro",
        "center-right / conservative",
        "https://www.lefigaro.fr/rss/figaro_actualites.xml",
    ),
    (
        "Libération",
        "left / progressive",
        "https://www.liberation.fr/arc/outboundfeeds/rss-all/?outputType=xml",
    ),
    (
        "La Croix",
        "Catholic humanist / moderate",
        "https://www.la-croix.com/RSS/UNIVERS",
    ),
    ("L'Humanité", "communist / far-left", "https://www.humanite.fr/rss"),
    ("Mediapart", "investigative left", "https://www.mediapart.fr/articles/feed"),
    ("Marianne", "republican sovereignist / mixed", "https://www.marianne.net/rss.xml"),
    ("Le Point", "center-right liberal", "https://www.lepoint.fr/rss.xml"),
    ("L'Obs", "center-left", "https://www.nouvelobs.com/rss.xml"),
    (
        "Les Échos",
        "pro-business / liberal economics",
        "https://www.lesechos.fr/rss/rss_une.xml",
    ),
    (
        "Le Monde diplomatique",
        "left intellectual / anti-globalization",
        "https://mondediplo.com/backend",
    ),
    (
        "Valeurs actuelles",
        "conservative / right-wing",
        "https://www.valeursactuelles.com/feed/",
    ),
    (
        "Le Parisien",
        "mainstream populist-centrist",
        "https://feeds.leparisien.fr/leparisien/rss",
    ),
    (
        "Courrier international",
        "international press curation / centrist",
        "https://www.courrierinternational.com/feed/all/rss.xml",
    ),
    ("Charlie Hebdo", "satirical / libertarian left", "https://charliehebdo.fr/feed/"),
]

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def main() -> None:
    now = datetime.now(timezone.utc)
    rows = []

    for outlet, profile, url in OUTLETS:
        print(f"Fetching {outlet} ...")
        feed = feedparser.parse(url)
        for entry in feed.entries:
            published = None
            if entry.get("published_parsed"):
                published = datetime(*entry.published_parsed[:6])

            rows.append(
                {
                    "outlet": outlet,
                    "editorial_profile": profile,
                    "feed_title": feed.feed.get("title", ""),
                    "feed_link": feed.feed.get("link", ""),
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": published,
                    "summary": entry.get("summary", ""),
                    "extracted_at": now,
                }
            )

    df = pl.DataFrame(rows)
    out_path = DATA_DIR / f"extracted_{now.strftime('%Y%m%d_%H%M%S')}.parquet"
    df.write_parquet(out_path)
    print(f"\nDone — {df.height} entries written to {out_path}")


if __name__ == "__main__":
    main()
