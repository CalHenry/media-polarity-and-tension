import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from src.ingestion.feeds import extract_feeds
from src.ingestion.process import clean_data

LOG_DIR = Path(__file__).resolve().parent / "logs"
STATUS_DIR = Path(__file__).resolve().parent / "status"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_DIR / "pipeline.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("pipeline")


def run() -> None:
    LOG_DIR.mkdir(exist_ok=True)
    STATUS_DIR.mkdir(exist_ok=True)

    t0 = time.time()
    logger.info("=" * 50)
    logger.info("Pipeline started")

    logger.info("Phase 1/2 — Extraction")
    t1 = time.time()
    r1 = extract_feeds()
    dt1 = time.time() - t1
    ok1 = r1.get("status") == "success"
    logger.info(
        "Extraction %s (%d entries, %d outlets, %.1fs)",
        "OK" if ok1 else "FAILED",
        r1.get("entries", 0),
        r1.get("outlets", 0),
        dt1,
    )
    if not ok1:
        aborted(t0, "extraction failure")
        sys.exit(1)

    logger.info("Phase 2/2 — Deduplication")
    t2 = time.time()
    new_raw_path = r1.get("output_path")
    r2 = clean_data(new_raw_path=new_raw_path)
    dt2 = time.time() - t2
    ok2 = r2.get("status") == "success"
    logger.info(
        "Deduplication %s (%d entries, %d outlets, %d duplicates removed, %.1fs)",
        "OK" if ok2 else "FAILED",
        r2.get("entries", 0),
        r2.get("outlets", 0),
        r2.get("duplicates_removed", 0),
        dt2,
    )
    if not ok2:
        aborted(t0, "deduplication failure")
        sys.exit(1)

    dt = time.time() - t0
    logger.info("Pipeline finished in %.1fs", dt)

    records_extracted = r1["entries"]
    duplicates_removed = r2["duplicates_removed"]
    new_records = records_extracted - duplicates_removed

    processed_dir = Path(__file__).resolve().parent / "data" / "processed"
    output_size_bytes = sum(f.stat().st_size for f in processed_dir.glob("*.parquet"))
    output_size_mb = round(output_size_bytes / (1024 * 1024), 1)

    status = {
        "last_run": datetime.now(timezone.utc).isoformat(),
        "status": "success",
        "records_extracted": records_extracted,
        "duplicates_removed": duplicates_removed,
        "new_records": new_records,
        "runtime_seconds": round(dt, 1),
        "output_size_mb": output_size_mb,
    }
    with open(STATUS_DIR / "status.json", "w") as f:
        json.dump(status, f, indent=2)
    logger.info("Status written to %s", STATUS_DIR / "status.json")


def aborted(t0: float, reason: str) -> None:
    dt = time.time() - t0
    status = {
        "last_run": datetime.now(timezone.utc).isoformat(),
        "status": "error",
        "reason": reason,
        "records_extracted": 0,
        "duplicates_removed": 0,
        "new_records": 0,
        "runtime_seconds": round(dt, 1),
        "output_size_mb": 0.0,
    }
    with open(STATUS_DIR / "status.json", "w") as f:
        json.dump(status, f, indent=2)
    logger.error("Pipeline aborted after %.1fs: %s", dt, reason)


if __name__ == "__main__":
    run()
