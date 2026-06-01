import logging
import sys
from pathlib import Path

import polars as pl

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _sanitize(name: str) -> str:
    return name.replace(" ", "_").replace("'", "_").replace("’", "_")


def clean_data(new_raw_path: str | None = None, language: str = "fr") -> dict:
    raw_dir = BASE_DIR / "data" / "raw" / language
    processed_dir = BASE_DIR / "data" / "processed" / language
    processed_dir.mkdir(parents=True, exist_ok=True)

    raw_files = sorted(raw_dir.glob("extracted_*.parquet"))

    all_parquet = list(raw_dir.glob("*.parquet"))
    unmatched = [f.name for f in all_parquet if not f.name.startswith("extracted_")]
    if unmatched:
        logger.warning(
            "Found %d parquet file(s) in %s that don't match pattern "
            "'extracted_*.parquet' and will be skipped: %s",
            len(unmatched),
            raw_dir,
            unmatched,
        )

    if not raw_files:
        logger.warning("No raw extraction files found")
        return {
            "status": "success",
            "outlets": 0,
            "entries": 0,
            "duplicates_removed": 0,
        }

    frames = []
    for f in raw_files:
        try:
            frames.append(pl.read_parquet(f))
        except Exception:
            logger.warning("Skipping corrupt or invalid file during read: %s", f)
    if not frames:
        logger.warning("No valid raw extraction files could be read")
        return {
            "status": "success",
            "outlets": 0,
            "entries": 0,
            "duplicates_removed": 0,
        }

    raw = pl.concat(frames)
    outlets = raw["outlet"].unique()
    total_entries = 0
    duplicates_removed = 0

    new_batch = None
    if new_raw_path and Path(new_raw_path).exists():
        new_batch = pl.read_parquet(new_raw_path)

    for outlet in outlets:
        new_rows = raw.filter(pl.col("outlet") == outlet)
        path = processed_dir / f"{_sanitize(outlet)}.parquet"

        if path.exists():
            existing = pl.read_parquet(path)

            if new_batch is not None:
                new_links = new_batch.filter(pl.col("outlet") == outlet)["link"]
                dup_count = new_links.is_in(existing["link"]).sum()
                duplicates_removed += dup_count

            combined = pl.concat([existing, new_rows])
        else:
            combined = new_rows

        deduped = combined.sort("extracted_at").unique(subset=["link"], keep="first")
        deduped.write_parquet(path)
        total_entries += deduped.height
        logger.info("  %s: %d entries", outlet, deduped.height)

    logger.info(
        "Done — %d entries across %d outlets (%d duplicates removed)",
        total_entries,
        len(outlets),
        duplicates_removed,
    )
    return {
        "status": "success",
        "outlets": len(outlets),
        "entries": total_entries,
        "duplicates_removed": duplicates_removed,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--language", default="fr", choices=["fr", "en"])
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    result = clean_data(language=args.language)
    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()
