import logging
import sys
from pathlib import Path

import polars as pl

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

logger = logging.getLogger(__name__)


def _sanitize(name: str) -> str:
    return name.replace(" ", "_").replace("'", "_").replace("’", "_")


def clean_data(new_raw_path: str | None = None) -> dict:
    PROCESSED_DIR.mkdir(exist_ok=True)

    raw_files = sorted(RAW_DIR.glob("extracted_*.parquet"))
    if not raw_files:
        logger.warning("No raw extraction files found")
        return {"status": "success", "outlets": 0, "entries": 0, "duplicates_removed": 0}

    raw = pl.concat(pl.read_parquet(f) for f in raw_files)
    outlets = raw["outlet"].unique()
    total_entries = 0
    duplicates_removed = 0

    new_batch = None
    if new_raw_path and Path(new_raw_path).exists():
        new_batch = pl.read_parquet(new_raw_path)

    for outlet in outlets:
        new_rows = raw.filter(pl.col("outlet") == outlet)
        path = PROCESSED_DIR / f"{_sanitize(outlet)}.parquet"

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
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    result = clean_data()
    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()
