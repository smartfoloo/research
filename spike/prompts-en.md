# Prompt text (English) — final, human-authored

EN-human prompts, written by the researcher (not AI-drafted — see CLAUDE.md,
EN-human must be genuinely human-authored or the condition label is false).

**Every task has a worked example.**

## Simple

1. **business-days** — Write a Python function named `business_days(date1, date2)`.
   Both dates are strings in `YYYY-MM-DD` format. The function should return the
   number of business days (Monday to Friday) between the two dates, without
   including the two dates. Ignore holidays. (Ex. `"2024-01-01", "2024-01-08"`
   → `4`)

2. **currency-format** — Write a Python function named `format_currency(n)`
   that returns `n` formatted as a string with a `$` in front of it and commas
   every 3 digits. For negative numbers, put a minus sign before the dollar
   sign. (Ex. `4640039` → `"$4,640,039"`)

3. **reverse-list-elements** — Write a Python function named
   `reverse_list_elements(elements, punctuation)` that reverses the order of
   `elements`. Make sure it keeps each punctuation mark in `punctuation`
   attached to its original element, and returns `(new_elements,
   new_punctuation)`. (Ex. `elements=["Hello", "world"], punctuation=["", "!"]`
   → `(["world", "Hello"], ["!", ""])`)

## Complex

4. **eval-expression** — Write a Python function named `eval_expression(expr)`
   that evaluates the expression in `expr`. Make sure to follow the order of
   operations with parenthesis and support negative numbers. If there is a
   division by zero, raise a `ZeroDivisionError`. (Ex. `"3 + 4 * (2 - 1)"` →
   `7`)

5. **shortest-path** — Write a Python function named
   `shortest_path(edges, start, end)` where `edges` is a list of
   `(from_node, to_node, weight)` tuples representing one-way roads. The
   function should return `(distance, path)`, the shortest total distance and
   an ordered list of nodes on that path. If `start` and `end` are the same
   node, return `(0, [start])`. If any edge weight is negative, give a
   `ValueError`. If no path exists, just return `(None, None)`. (Ex.
   `edges=[("A","B",1), ("B","C",2), ("A","C",5)]`, `start="A"`, `end="C"` →
   `(3, ["A", "B", "C"])`)

6. **bank-rollback** — Write a Python function named
   `bank_rollback(balance, transactions)` where `transactions` is an ordered
   number list of transaction amounts. Apply them in order in a single turn.
   If any transaction make the balance negative, just reject the entire list
   and return `(balance, False)` where `balance` is the original balance.
   Otherwise return `(final_balance, True)`. (Ex. `balance=100,
   transactions=[50, -30, -200]` → `(100, False)`)
