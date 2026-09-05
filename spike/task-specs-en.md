# Task specs (English, neutral) — spike v1

Each spec is the ground truth for what "correct" means. Write JA-raw from
these directly (not by translating an English *prompt* — these are specs, the
actual prompt wording is a separate step). Use these to write test cases too.

---

## Simple

### 1. reverse-list-elements
**Reframed 2026-09-01 — see note below.** Given a list of string elements and
a parallel list of punctuation marks (one per element, may be empty), reverse
the order of the elements while keeping each punctuation mark attached to the
element it was originally paired with.
- Input: a list of strings, a parallel list of punctuation marks (some may
  be `""`).
- Output: a list with element order reversed, punctuation still paired
  correctly.
- Edge cases: single element; empty list; all elements have punctuation;
  none do.
- Example: elements `["Hello", "world"]`, punctuation `["", "!"]` →
  elements `["world", "Hello"]`, punctuation `["!", ""]`.

**Why reframed:** the original version ("reverse the words in this
sentence") assumes whitespace-delimited word boundaries, which English has
for free and Japanese does not — Japanese word segmentation requires a
morphological analyzer and is itself linguistically nontrivial. That version
would silently test word segmentation in the JA condition and not in the EN
condition — a task-construct confound, not a language-comprehension effect.
Using a pre-segmented array as input tests the same reversal/pairing logic
in both languages without depending on either language's word-boundary
conventions.

### 2. dedupe-and-sort-list
Given a list of integers, remove duplicates and return them sorted ascending.
- Input: a list of integers (may contain duplicates, negatives, unsorted).
- Output: a list of unique integers, ascending.
- Edge cases: empty list; all duplicates; already sorted; single element.

### 3. business-days-between-dates
Given two dates, return the number of business days (Mon–Fri) between them,
excluding both endpoints. No public holidays considered.
- Input: two dates (specify a format, e.g. `YYYY-MM-DD`).
- Output: an integer count of business days strictly between the two dates.
- Edge cases: same date given twice (→ 0); start date after end date (define
  behavior: error or negative count — pick one and state it); dates spanning
  a weekend only.

### 4. validate-email-format
Given a string, return whether it is a syntactically valid email address.
- Input: a single string.
- Output: boolean.
- Rules to specify explicitly: must have exactly one `@`; local part
  non-empty; domain part contains at least one `.`; no spaces anywhere.
- Edge cases: multiple `@`; missing domain; leading/trailing whitespace;
  empty string.

### 5. format-number-as-currency
Given an integer, return it as a string with comma group separators and a
leading `$`.
- Input: an integer (can be negative).
- Output: a string, e.g. `1234567` → `"$1,234,567"`.
- Edge cases: negative numbers (define exact format, e.g. `"-$1,234"`); zero;
  numbers under 1000 (no comma needed).

---

## Complex

### 6. expression-evaluator-with-precedence
Given a string containing a math expression with `+ - * /`, parentheses, and
integers, evaluate it respecting standard operator precedence and
parentheses.
- Input: a string, e.g. `"3 + 4 * (2 - 1)"`.
- Output: the numeric result.
- Requirements: correct precedence (`*` `/` before `+` `-`); support nested
  parentheses; support unary minus (e.g. `-3 + 4`); division by zero must be
  handled explicitly (define: raise an error / return a specific value —
  pick one and state it).
- Edge cases: single number with no operators; deeply nested parens;
  division by zero.

### 7. lru-cache-with-ttl
Implement a fixed-capacity cache with two eviction mechanisms: least-recently-
used (LRU) eviction when full, and time-to-live (TTL) expiry per entry.
- Operations: `put(key, value, ttl_seconds)`, `get(key)` → value or "not
  found" (also define: does `get` on expired-but-not-yet-evicted count as a
  miss?).
- Requirement: `get` and `put` both count as "used" for LRU purposes.
- Edge case to resolve explicitly in the spec: when capacity is full and the
  entry that would be LRU-evicted has *also* expired — what happens, and does
  it matter for this task? (State the rule so every model is judged the same
  way.)

### 8. shortest-path-with-route
Given a weighted, directed graph and two nodes, return both the shortest
distance and the actual sequence of nodes on that path.
- Input: a graph (edge list with weights), a start node, an end node.
- Output: total distance and the ordered list of nodes in the path.
- Requirements: reject negative edge weights explicitly (define what to
  return/raise); if no path exists, define what to return.
- Edge cases: start == end; disconnected graph; multiple equal-length shortest
  paths (any valid one is acceptable — state this).

### 9. bank-transactions-with-rollback
Given a starting balance and an ordered list of transactions (deposits and
withdrawals), apply them as a single atomic batch: if any withdrawal in the
sequence would overdraw the account (balance goes negative) at the point it's
applied, reject the entire batch and return the original starting balance
unchanged. Otherwise return the final balance.
- Input: starting balance (integer), list of signed integers (positive =
  deposit, negative = withdrawal).
- Output: final balance, and a flag/indicator of whether the batch was
  applied or rejected.
- Edge cases: empty transaction list; a transaction that brings balance to
  exactly 0 (not negative — should succeed); the overdraft-triggering
  transaction being the very last one in the list.

### 10. meeting-room-scheduler
Given a list of meeting time intervals (start, end), determine the minimum
number of rooms required so that no two meetings assigned to the same room
overlap in time.
- Input: a list of (start, end) pairs, unsorted, integers or timestamps
  (specify units).
- Output: a single integer — the minimum number of rooms needed.
- Requirement to state explicitly: a meeting ending exactly when another
  starts (e.g. `[9,10]` and `[10,11]`) does NOT count as overlapping — they
  can share a room.
- Edge cases: empty list (→ 0); all meetings identical time (→ N rooms for N
  meetings); no overlaps at all (→ 1 room).

---

## Notes for whoever writes prompts from this

- Every "define X explicitly" above is a place where an ambiguous spec would
  let two correct implementations disagree — resolve these *before* writing
  prompts, not after seeing model output, or you'll be tempted to move the
  goalposts per-model.
- Each task needs a small test suite (5–10 cases covering the edge cases
  listed) written once, in a language-neutral form, and reused to grade every
  condition's output identically.
