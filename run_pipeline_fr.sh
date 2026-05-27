#!/bin/bash

cd /Users/calh/Developer/news-politics-score

/opt/homebrew/bin/uv run scripts/run_pipeline_fr.py \
  >> logs/pipeline_fr.log 2>&1
