import logging
import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path

import feedparser
import polars as pl

FR_OUTLETS: list[tuple[str, str, str]] = [
    ("Le Monde", "center / liberal establishment", "https://www.lemonde.fr/rss/une.xml"),
    ("Le Figaro", "center-right / conservative", "https://www.lefigaro.fr/rss/figaro_actualites.xml"),
    ("Libération", "left / progressive", "https://www.liberation.fr/arc/outboundfeeds/rss-all/?outputType=xml"),
    ("La Croix", "Catholic humanist / moderate", "https://www.la-croix.com/RSS/UNIVERS"),
    ("L'Humanité", "communist / far-left", "https://www.humanite.fr/rss"),
    ("Mediapart", "investigative left", "https://www.mediapart.fr/articles/feed"),
    ("Marianne", "republican sovereignist / mixed", "https://www.marianne.net/rss.xml"),
    ("Le Point", "center-right liberal", "https://www.lepoint.fr/rss.xml"),
    ("L'Obs", "center-left", "https://www.nouvelobs.com/rss.xml"),
    ("Les Échos", "pro-business / liberal economics", "https://www.lesechos.fr/rss/rss_une.xml"),
    ("Le Monde diplomatique", "left intellectual / anti-globalization", "https://mondediplo.com/backend"),
    ("Valeurs actuelles", "conservative / right-wing", "https://www.valeursactuelles.com/feed/"),
    ("Le Parisien", "mainstream populist-centrist", "https://feeds.leparisien.fr/leparisien/rss"),
    ("Courrier international", "international press curation / centrist", "https://www.courrierinternational.com/feed/all/rss.xml"),
    ("Charlie Hebdo", "satirical / libertarian left", "https://charliehebdo.fr/feed/"),
]

EN_OUTLETS: list[tuple[str, str, str]] = [
    ("Jacobin", "Democratic socialist / left", "https://jacobin.com/feed"),
    ("Mother Jones", "Progressive investigative", "https://www.motherjones.com/feed/"),
    ("The Nation", "Left-wing", "https://www.thenation.com/feed/"),
    ("The Guardian", "Center-left", "https://www.theguardian.com/world/rss"),
    ("Current Affairs", "Left intellectual / cultural", "https://www.currentaffairs.org/feed"),
    ("Reuters", "Center / wire service", "https://feeds.reuters.com/Reuters/worldNews"),
    ("Associated Press", "Center / factual reporting", "https://feeds.apnews.com/rss/apf-topnews"),
    ("NPR", "Center-left public media", "https://feeds.npr.org/1001/rss.xml"),
    ("Financial Times", "Establishment center / liberal economics", "https://www.ft.com/world?format=rss"),
    ("The Economist", "Centrist / classical liberal", "https://www.economist.com/international/rss.xml"),
    ("Semafor", "Centrist / global affairs", "https://www.semafor.com/feed"),
    ("National Review", "Conservative", "https://www.nationalreview.com/feed/"),
    ("The Spectator", "Conservative / liberal-conservative", "https://www.spectator.co.uk/feed/"),
    ("The American Conservative", "Paleoconservative / anti-interventionist", "https://www.theamericanconservative.com/feed/"),
    ("Reason", "Libertarian", "https://reason.com/feed/"),
    ("Fox News", "Mainstream conservative", "https://moxie.foxnews.com/google-publisher/politics.xml"),
    ("ProPublica", "Investigative / nonpartisan", "https://www.propublica.org/feeds/propublica/main"),
    ("The Intercept", "Civil-libertarian / left investigative", "https://theintercept.com/feed/?lang=en"),
    ("UnHerd", "Heterodox / anti-establishment", "https://unherd.com/feed/"),
    ("Compact", "Post-liberal / heterodox", "https://compactmag.com/rss.xml"),
]

# backward compat alias
OUTLETS = FR_OUTLETS

logger = logging.getLogger(__name__)


def extract_feeds(
    outlets: Sequence[tuple[str, str, str]] = FR_OUTLETS,
    language: str = "fr",
) -> dict:
    now = datetime.now(timezone.utc)
    rows = []
    outlets_fetched = 0

    for outlet, profile, url in outlets:
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

    raw_dir = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / language
    raw_dir.mkdir(parents=True, exist_ok=True)
    df = pl.DataFrame(rows)
    out_path = raw_dir / f"extracted_{now.strftime('%Y%m%d_%H%M%S')}.parquet"
    df.write_parquet(out_path)
    logger.info("Done — %d entries written to %s", df.height, out_path)
    return {
        "status": "success",
        "entries": df.height,
        "outlets": outlets_fetched,
        "output_path": str(out_path),
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--language", default="fr", choices=["fr", "en"])
    parser.add_argument("--outlets", default=None, help="Comma-separated outlet names to fetch (default: all)")
    args = parser.parse_args()

    outlets = EN_OUTLETS if args.language == "en" else FR_OUTLETS

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    result = extract_feeds(outlets=outlets, language=args.language)
    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()
