# Raw Google Translate output (JA→EN), verbatim — 2026-09-07

Captured live from translate.google.com by pasting each task's `ja_raw` text
from `spike/prompts.json` and copying the English output verbatim, to check
whether the `mt_en` field currently stored in `prompts.json` matches what
Google Translate actually produces.

**Finding:** live Google Translate preserves backticks around every
identifier/value in all 5 tasks whose `ja_raw` uses them. The `mt_en` stored
in `prompts.json` has zero backticks in all 5 of those tasks — the stripping
happened somewhere between running the translation and saving it, not in
Google Translate itself. `business-days` is not part of this problem: its
`ja_raw` never had backticks to begin with.

## business-days

Create a Python function called business_days(date1, date2) that returns the number of business days (Monday to Friday) between two dates. Both dates are in YYYY-MM-DD format. Please calculate only the days of the week without taking into account holidays. However, please do not include the two dates themselves. (Example: "2024-01-01", "2024-01-08" → 4).

## currency-format

Create a Python function called `format_currency(n)` that returns `n` with a `$` at the beginning and every three digits separated by commas. For negative numbers, be sure to include a minus sign before the dollar sign. (Example: `4640039` -> "$4,640,039")

## reverse-list-elements

Create a Python function called `reverse_list_elements(elements, punctuation)` that reverses the order of `elements`. In that case, please set the symbols included in `punctuation` with the original word and return `(new_elements, new_punctuation)`. (Example: `elements=["Hello", "world"]`, `punctuation=["", "!"]` -> `(["world", "Hello"], ["!", ""])`)

## eval-expression

Create a Python function called `eval_expression(expr)` that computes the expression `expr`. Be sure to consider the order of operations and be able to calculate negative numbers. When dividing by zero, raise `ZeroDivisionError`. (Example: `"3 + 4 * (2 - 1)"` -> `7`)

## shortest-path

Create a Python function called `shortest_path(edges, start, end)` that returns the shortest total distance and a list `(distance, path)` of the nodes along the path. `edges` is a list of tuples `(from_node, to_node, weight)` representing a one-way street. If start and end are the same node, return (0, [start]). If the weight of any edge is negative, raise `ValueError`. If the route does not exist, return `(None, None)`. (Example: `edges=[("A","B",1), ("B","C",2), ("A","C",5)]`, `start="A"`, `end="C"` -> `(3, ["A", "B", "C"])`)

## bank-rollback

Create a Python function called `bank_rollback(balance, transactions)`. `transactions` is a numeric list of transaction amounts. Try to apply the given transactions in order and return the calculated final balance. If the balance becomes negative even during calculation, stop the calculation and return `(balance, False)` using the original balance `balance`. Otherwise, return `(final_balance, True)`. (Example: `balance=100, transactions=[50, -30, -200]` -> `(100, False)`)
