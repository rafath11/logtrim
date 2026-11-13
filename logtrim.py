#!/usr/bin/env python3
"""logtrim - summarize a big log file: counts by error pattern, top offenders, time range.
Zero-dependency Python 3.8+. Reads the file you give it; never modifies it.
Exit codes: 0 = summarized, no ERROR/CRITICAL lines; 1 = ERROR/CRITICAL lines found; 2 = usage/file error.
"""
import argparse, re, sys
from collections import Counter

LEVELS = ["DEBUG", "INFO", "WARNING", "WARN", "ERROR", "CRITICAL"]
TS_RE = re.compile(r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})")
LEVEL_RE = re.compile(r"\b(DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL)\b")
DIGITS_RE = re.compile(r"\d+")
SPACE_RE = re.compile(r"\s+")

def normalize(line):
    line = TS_RE.sub("<ts>", line)
    line = DIGITS_RE.sub("<n>", line)
    return SPACE_RE.sub(" ", line).strip()[:160]

def main():
    ap = argparse.ArgumentParser(description="Summarize a log file: level counts, top error patterns, time range.")
    ap.add_argument("file", help="log file to summarize (plain text)")
    ap.add_argument("--top", type=int, default=10, help="error patterns to show (default: 10)")
    args = ap.parse_args()
    try:
        fh = open(args.file, encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"error: cannot read {args.file}: {e}", file=sys.stderr); return 2
    total = 0; levels = Counter(); patterns = Counter(); first_ts = None; last_ts = None
    with fh:
        for raw in fh:
            total += 1
            m = TS_RE.search(raw)
            if m:
                ts = m.group(1)
                if first_ts is None: first_ts = ts
                last_ts = ts
            lm = LEVEL_RE.search(raw)
            lvl = lm.group(1) if lm else "NONE"
            if lvl == "WARN": lvl = "WARNING"
            levels[lvl] += 1
            if lvl in ("ERROR", "CRITICAL"):
                patterns[normalize(raw)] += 1
    print(f"File:        {args.file}")
    print(f"Lines:       {total}")
    print(f"Time range:  {first_ts or 'no timestamps found'} -> {last_ts or ''}".rstrip())
    print("\nBy level:")
    for lvl in LEVELS + ["NONE"]:
        if levels.get(lvl): print(f"  {lvl:<9} {levels[lvl]}")
    err = levels.get("ERROR", 0) + levels.get("CRITICAL", 0)
    print(f"\nTop error patterns (of {err} ERROR/CRITICAL lines):")
    if not patterns: print("  (none)")
    for pat, n in patterns.most_common(args.top): print(f"  {n:>6}  {pat}")
    return 1 if err else 0

if __name__ == "__main__":
    sys.exit(main())
