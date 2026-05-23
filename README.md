# News politics score


## Data extraction and pipeline

Data is extracted from RSS feeds.  

A simple pipeline, extract the feeds, then process the data (remove duplicates, sort entries by origin into seperate files). All the data is stored in parquet files.

A launchd job is running on my mac to run the pipeline every day.
