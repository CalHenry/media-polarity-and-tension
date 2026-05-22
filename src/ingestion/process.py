"""Deduplicate extracted RSS feed data, writing one parquet file per outlet."""

from pathlib import Path

import polars as pl

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"


def _sanitize(name: str) -> str:
    return name.replace(" ", "_").replace("'", "_").replace("’", "_")


def main() -> None:
    PROCESSED_DIR.mkdir(exist_ok=True)

    raw_files = sorted(DATA_DIR.glob("extracted_*.parquet"))
    if not raw_files:
        print("No raw extraction files found.")
        return

    raw = pl.concat(pl.read_parquet(f) for f in raw_files)
    outlets = raw["outlet"].unique()

    for outlet in outlets:
        new_rows = raw.filter(pl.col("outlet") == outlet)
        path = PROCESSED_DIR / f"{_sanitize(outlet)}.parquet"

        if path.exists():
            existing = pl.read_parquet(path)
            combined = pl.concat([existing, new_rows])
        else:
            combined = new_rows

        deduped = combined.sort("extracted_at").unique(subset=["link"], keep="first")
        deduped.write_parquet(path)
        print(f"  {outlet}: {deduped.height} entries → {path.name}")


if __name__ == "__main__":
    main()
