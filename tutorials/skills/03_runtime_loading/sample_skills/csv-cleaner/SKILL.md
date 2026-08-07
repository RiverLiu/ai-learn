---
name: csv-cleaner
description: Clean, validate, normalize, and summarize CSV files. Use when the user asks to inspect tabular data, fix malformed rows, normalize columns, detect missing values, or produce cleaned CSV outputs.
---

# CSV Cleaner

Workflow:

1. Inspect the delimiter, header row, encoding, and row count.
2. Preserve the original file unless the user explicitly asks to overwrite it.
3. Normalize column names to snake_case.
4. Report missing values, duplicate rows, suspicious numeric values, and changed columns.
5. Write cleaned output to a new file.
