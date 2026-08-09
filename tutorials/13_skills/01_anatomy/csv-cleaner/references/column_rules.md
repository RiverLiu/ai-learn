# Column Rules

Use these rules when normalizing CSV column names.

## Naming

- Convert column names to `snake_case`.
- Trim leading and trailing whitespace.
- Replace spaces, hyphens, and repeated punctuation with a single underscore.
- Keep names short but meaningful.
- Avoid ambiguous names such as `value`, `data`, `info`, and `misc` unless the source data gives no better meaning.

## Common Renames

| Source column | Normalized column |
| --- | --- |
| `Customer ID` | `customer_id` |
| `Customer Name` | `customer_name` |
| `Order Date` | `order_date` |
| `Order Amount` | `order_amount` |
| `Email Address` | `email` |
| `Phone Number` | `phone` |

## Reporting

When reporting changes, include:

- Original column names.
- Normalized column names.
- Columns with missing values.
- Columns that still need human interpretation.
