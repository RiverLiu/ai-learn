---
name: csv-cleaner
description: Clean, validate, normalize, and summarize CSV files. Use when the user asks Codex to inspect tabular data, fix malformed rows, normalize column names, detect missing values, or produce cleaned CSV outputs.
---

# CSV Cleaner

Start by running `scripts/profile_csv.py` on the input file to inspect delimiter, headers, row count,
missing values, duplicate rows, and suspicious columns.

For project-specific column naming rules, read `references/column_rules.md`.

When cleaning CSV files:

1. Inspect the header and delimiter first.
2. Preserve the original file unless the user explicitly asks to overwrite it.
3. Normalize column names before changing row values.
4. Write cleaned output to a new file.
5. Report row counts, changed columns, dropped rows, and unresolved anomalies.

Never overwrite the source CSV unless the user explicitly asks for it.
