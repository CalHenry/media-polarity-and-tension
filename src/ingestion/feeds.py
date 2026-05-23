import logging
import sys
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

RAW_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"


logger = logging.getLogger(__name__)


def extract_feeds() -> dict:
    now = datetime.now(timezone.utc)
    rows = []
    outlets_fetched = 0

    for outlet, profile, url in OUTLETS:
        logger.info("Fetching %s ...", outlet)
        try:
            feed = feedparser.parse(url)
            outlets_fetched += 1
        except Exception:
            logger.exception("Failed to fetch %s", outlet)
            continue

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

    if not rows:
        logger.error("No entries extracted from any outlet")
        return {"status": "error", "error": "No entries extracted", "entries": 0}

    df = pl.DataFrame(rows)
    out_path = RAW_DATA_DIR / f"extracted_{now.strftime('%Y%m%d_%H%M%S')}.parquet"
    df.write_parquet(out_path)
    logger.info("Done — %d entries written to %s", df.height, out_path)
    return {
        "status": "success",
        "entries": df.height,
        "outlets": outlets_fetched,
        "output_path": str(out_path),
    }


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    result = extract_feeds()
    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()
