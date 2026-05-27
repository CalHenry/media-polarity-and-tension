#!/bin/bash

cd /Users/calh/Developer/news-politics-score

/opt/homebrew/bin/uv run scripts/run_pipeline_en.py \
  >> logs/pipeline_en.log 2>&1
