#!/usr/bin/env python3
"""
Convert NRC Emotion Lexicon TSV to JSON format using Polars.

The French-NRC-EmoLex.txt file has the format:
English Word\tanger\tanticipation\tdisgust\tfear\tjoy\tnegative\tpositive\tsadness\tsurprise\ttrust\tFrench Word

This script converts it to JSON dictionaries where:
- Keys are French words (last column)
- Values are the emotion scores (you can specify which emotion column to use)

Usage:
    python scripts/convert_emolex_to_json.py --emotion anger
    python scripts/convert_emolex_to_json.py --emotion fear
    python scripts/convert_emolex_to_json.py --all-emotions
"""

import argparse
import json
from pathlib import Path

import polars as pl

EMOTIONS = [
    "anger", "anticipation", "disgust", "fear", "joy",
    "negative", "positive", "sadness", "surprise", "trust",
]

FRENCH_COL = "French Word"


def read_emolex_tsv(filepath: Path) -> pl.LazyFrame:
    """Read the EmoLex TSV file and return a LazyFrame for deferred execution."""
    return pl.scan_csv(filepath, separator="\t", encoding="utf-8")


def extract_emotion(lf: pl.LazyFrame, emotion: str, include_zero: bool = False) -> dict[str, int]:
    """
    Extract a single emotion from the lexicon as a {french_word: score} dict.

    Uses a lazy chain: filter nulls/empties → optionally filter zeros
    → select only the two needed columns → collect → to_dict.
    """
    if emotion not in EMOTIONS:
        raise ValueError(f"Unknown emotion: {emotion!r}. Available: {EMOTIONS}")

    result = (
        lf
        .filter(pl.col(FRENCH_COL).is_not_null() & pl.col(FRENCH_COL).str.len_chars().gt(0)) #gt() = equivalent of “greater than” operator
        .filter(pl.col(emotion).gt(0) if not include_zero else pl.lit(True))
        .select(FRENCH_COL, emotion)
        .collect()
    )

    # series_to_dict: one shot, no Python-level iteration
    words  = result[FRENCH_COL]
    scores = result[emotion]
    return dict(zip(words.to_list(), scores.to_list()))


def write_json(lexicon: dict, output_path: Path) -> None:
    """Serialize the lexicon dict to a pretty-printed JSON file."""
    output_path.write_text(json.dumps(lexicon, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Convert NRC EmoLex TSV to JSON (Polars)")
    parser.add_argument("--emotion", choices=EMOTIONS, default="anger",
                        help="Which emotion to extract (default: anger)")
    parser.add_argument("--input", type=str, default="data/lexicons/fr/French-NRC-EmoLex.txt",
                        help="Path to input TSV file")
    parser.add_argument("--output", type=str, default=None,
                        help="Path to output JSON file (default: data/lexicons/fr/emotion_{emotion}.json)")
    parser.add_argument("--include-zero", action="store_true",
                        help="Include words with score 0")
    parser.add_argument("--all-emotions", action="store_true",
                        help="Generate JSON files for all emotions")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return

    # LazyFrame is shared across all emotion extractions — scan happens once
    lf = read_emolex_tsv(input_path)

    emotions_to_run = EMOTIONS if args.all_emotions else [args.emotion]

    for emotion in emotions_to_run:
        output_path = (
            Path(args.output) if (args.output and not args.all_emotions)
            else Path(f"data/lexicons/fr/emotion_{emotion}.json")
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)

        lexicon = extract_emotion(lf, emotion, args.include_zero)
        write_json(lexicon, output_path)
        print(f"[{emotion:>12}]  {len(lexicon):>5} entries  →  {output_path}")

    if not args.all_emotions:
        lexicon = extract_emotion(lf, args.emotion, args.include_zero)
        sample = list(lexicon.items())[:5]
        print("\nSample entries:")
        for word, score in sample:
            print(f"  {word}: {score}")


if __name__ == "__main__":
    main()
