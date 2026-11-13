# logtrim

**The problem:** a job fails overnight and the log is 40,000 lines. Reading it top to bottom is not a plan.

**The fix:** summarize first — how many errors, of what kind, and when — then read only what matters.

`logtrim` is a single-file, zero-dependency Python script. Give it a log file and it reports the time range covered, line counts by level (DEBUG/INFO/WARNING/ERROR/CRITICAL), and the top ERROR/CRITICAL patterns with timestamps and numbers normalized away, so repeated failures group together instead of filling the screen one by one.

## Quick start

```bash
python3 logtrim.py app.log
python3 logtrim.py app.log --top 5
```

Example output (from `sample.log`):

```
File:        sample.log
Lines:       7
Time range:  2026-11-10 01:12:03 -> 2026-11-10 01:16:01

By level:
  INFO      3
  WARNING   1
  ERROR     3

Top error patterns (of 3 ERROR/CRITICAL lines):
       2  <ts> ERROR connection to db host <n>.<n>.<n>.<n> timed out after <n>s
       1  <ts> ERROR failed to open file /tmp/export<n>.csv
```

## How patterns are grouped

Timestamps and digit runs are replaced with `<ts>` / `<n>` before grouping, so the same failure at different times or against different hosts counts as one pattern. Lines without a recognized level count as NONE and never appear in the error patterns.

## What it deliberately does not do

- It never modifies, truncates, or deletes the log — read-only summarization.
- It does not parse every log format: timestamps are ISO-style (`2026-11-10 01:13:10` or with a `T`), and levels are the common uppercase words.
- It does not alert, tail, or ship logs anywhere.

## Exit codes (built for scripts and cron)

- `0` — summarized; no ERROR/CRITICAL lines found
- `1` — summarized; ERROR/CRITICAL lines present
- `2` — usage or file error

MIT licensed. Python 3.8+, no dependencies.
