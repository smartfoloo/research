# Prompt text (English) — short form for translation

The actual text to send to models. Self-contained: everything the model
needs is in the prompt itself — the task, the language, the exact function
name/signature to use, and one worked example. Nothing is assumed or left to
default behavior.

Language: **Python**, fixed across all tasks/conditions, so generated code
is comparable and gradable the same way regardless of prompt language.

Function/class names are fixed too, so grading can call a known name
directly instead of parsing arbitrary generated code.

**Every task has a worked example — verify each by hand before use.**

1. **reverse-list-elements** — Write a Python function named
   `reverse_list_elements(elements, punctuation)` that reverses the order of
   `elements`, keeping each punctuation mark in `punctuation` attached to its
   original element, and returns `(new_elements, new_punctuation)`. Example:
   `elements=["Hello", "world"], punctuation=["", "!"]` →
   `(["world", "Hello"], ["!", ""])`.

2. **dedupe-sort** — Write a Python function named `dedupe_sort(numbers)`
   that returns the unique values in `numbers`, sorted ascending. Example:
   `[3, 1, 2, 3, 1]` → `[1, 2, 3]`.

3. **business-days** — Write a Python function named
   `business_days(date1, date2)` where both dates are strings in
   `"YYYY-MM-DD"` format. Return the number of business days (Mon–Fri)
   strictly between the two dates, not including either date itself. Ignore
   holidays. Example: `"2024-01-01", "2024-01-08"` → `4`.

4. **valid-email** — Write a Python function named `is_valid_email(s)` that
   returns `True` if `s` is a valid email: exactly one `@`, non-empty text
   before it, and the part after it contains at least one `.`, with no
   spaces anywhere. Otherwise return `False`. Example:
   `"user@example.com"` → `True`; `"no-at-symbol.com"` → `False`.

5. **currency-format** — Write a Python function named
   `format_currency(n)` that returns `n` formatted as a string with a
   leading `$` and comma separators every 3 digits. Negative numbers: minus
   sign before the dollar sign. Example: `1234567` → `"$1,234,567"`;
   `-1234` → `"-$1,234"`.

6. **eval-expression** — Write a Python function named
   `eval_expression(expr)` that evaluates the arithmetic expression string
   `expr`, respecting standard operator precedence and parentheses, and
   supporting unary minus. If there is a division by zero, raise a
   `ZeroDivisionError`. Example: `"3 + 4 * (2 - 1)"` → `7`.

7. **lru-ttl-cache** — Write a Python class named `LRUTTLCache` with
   `__init__(self, capacity)`, `put(self, key, value, ttl_seconds)`, and
   `get(self, key)`. Both `put` and `get` count as recent use for LRU
   eviction. Entries also expire after their `ttl_seconds` regardless of
   use; `get` returns `None` for an expired entry even if not yet evicted.
   When full, evict the least-recently-used entry to make room. Example:
   `cache = LRUTTLCache(2)`; `cache.put("a", 1, 100)`; `cache.get("a")` →
   `1`.

8. **shortest-path** — Write a Python function named
   `shortest_path(edges, start, end)` where `edges` is a list of
   `(from_node, to_node, weight)` tuples for a directed graph. Return
   `(distance, path)`, the shortest total distance and the ordered list of
   nodes on that path. If any edge weight is negative, raise a
   `ValueError`. If no path exists, return `(None, None)`. Example:
   `edges=[("A","B",1), ("B","C",2), ("A","C",5)]`, `start="A"`, `end="C"` →
   `(3, ["A", "B", "C"])`.

9. **bank-rollback** — Write a Python function named
   `bank_rollback(balance, transactions)` where `transactions` is an ordered
   list of signed integers. Apply them in order as a single batch. If any
   transaction would make the balance negative, reject the entire batch and
   return `(balance, False)` — the original balance, unchanged. Otherwise
   return `(final_balance, True)`. Example: `balance=100,
   transactions=[50, -30, -200]` → `(100, False)`.

10. **meeting-rooms** — Write a Python function named
    `min_meeting_rooms(intervals)` where `intervals` is a list of
    `(start, end)` integer tuples. Return the minimum number of rooms
    needed so no two meetings in the same room overlap. A meeting ending
    exactly when another starts does not count as overlapping. Example:
    `[(9,10), (9,11), (10,12)]` → `2`.
