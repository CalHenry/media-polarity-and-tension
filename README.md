# News politics score


## Data extraction and pipeline

Data is extracted from RSS feeds.  

2 identical pipelines for 2 extractions in 2 languages:
- French press (from France)
- English language press (not only UK or US)

Simple pipeline:
- feeds.py: extract the data using feedparser, write the content to a single parquet file using polars in ```data/raw/{language}```
- process.py: gather all the extraction parquet files, concat, remove duplicates and sort entries by journal. Output to ```data/processed```
