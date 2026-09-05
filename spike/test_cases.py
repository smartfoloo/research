"""
Test cases per task. VERIFY THESE BY HAND before trusting grading results —
a wrong expected value silently fails every correct implementation.

Standard tasks: function_name(*args) is called, result compared to
`expected` with ==, unless `expect_exception` is set (exception class name
as a string), in which case the call must raise that exception type.

Task 7 (lru-ttl-cache) is stateful/sequential and doesn't fit the single
call/compare pattern, so it has its own scripted harness in CUSTOM_HARNESS
instead of an entry here.
"""

TEST_CASES = {
    "reverse-list-elements": {
        "function": "reverse_list_elements",
        "cases": [
            {"args": [["Hello", "world"], ["", "!"]],
             "expected": [["world", "Hello"], ["!", ""]]},
            {"args": [["only"], [""]],
             "expected": [["only"], [""]]},
            {"args": [[], []],
             "expected": [[], []]},
            {"args": [["a", "b", "c"], [",", ",", "."]],
             "expected": [["c", "b", "a"], [".", ",", ","]]},
        ],
    },

    "dedupe-sort": {
        "function": "dedupe_sort",
        "cases": [
            {"args": [[3, 1, 2, 3, 1]], "expected": [1, 2, 3]},
            {"args": [[]], "expected": []},
            {"args": [[5, 5, 5]], "expected": [5]},
            {"args": [[-1, -2, 0, -1]], "expected": [-2, -1, 0]},
        ],
    },

    "business-days": {
        "function": "business_days",
        "cases": [
            {"args": ["2024-01-01", "2024-01-08"], "expected": 4},
            {"args": ["2024-01-01", "2024-01-01"], "expected": 0},
            {"args": ["2024-01-06", "2024-01-08"], "expected": 0},
            {"args": ["2024-01-01", "2024-01-02"], "expected": 0},
        ],
    },

    "valid-email": {
        "function": "is_valid_email",
        "cases": [
            {"args": ["user@example.com"], "expected": True},
            {"args": ["no-at-symbol.com"], "expected": False},
            {"args": ["two@@example.com"], "expected": False},
            {"args": ["user@nodot"], "expected": False},
            {"args": ["us er@example.com"], "expected": False},
            {"args": ["@example.com"], "expected": False},
        ],
    },

    "currency-format": {
        "function": "format_currency",
        "cases": [
            {"args": [1234567], "expected": "$1,234,567"},
            {"args": [-1234], "expected": "-$1,234"},
            {"args": [0], "expected": "$0"},
            {"args": [999], "expected": "$999"},
        ],
    },

    "eval-expression": {
        "function": "eval_expression",
        "cases": [
            {"args": ["3 + 4 * (2 - 1)"], "expected": 7},
            {"args": ["-3 + 4"], "expected": 1},
            {"args": ["(2 + 3) * (4 - 2)"], "expected": 10},
            {"args": ["10 / 0"], "expect_exception": "ZeroDivisionError"},
        ],
    },

    "shortest-path": {
        "function": "shortest_path",
        "cases": [
            {"args": [[["A", "B", 1], ["B", "C", 2], ["A", "C", 5]], "A", "C"],
             "expected": [3, ["A", "B", "C"]]},
            {"args": [[["A", "B", 1]], "A", "B"],
             "expected": [1, ["A", "B"]]},
            {"args": [[["A", "B", 1]], "A", "C"],
             "expected": [None, None]},
            {"args": [[["A", "B", 1]], "A", "A"],
             "expected": [0, ["A"]]},
        ],
    },

    "bank-rollback": {
        "function": "bank_rollback",
        "cases": [
            {"args": [100, [50, -30, -200]], "expected": [100, False]},
            {"args": [100, [50, -30]], "expected": [120, True]},
            {"args": [100, []], "expected": [100, True]},
            {"args": [100, [-100]], "expected": [0, True]},
        ],
    },

    "meeting-rooms": {
        "function": "min_meeting_rooms",
        "cases": [
            {"args": [[[9, 10], [9, 11], [10, 12]]], "expected": 2},
            {"args": [[]], "expected": 0},
            {"args": [[[1, 5], [1, 5], [1, 5]]], "expected": 3},
            {"args": [[[1, 2], [2, 3], [3, 4]]], "expected": 1},
        ],
    },
}

# Task 7: stateful, scripted separately. This checks LRU eviction only —
# TTL expiry isn't exercised here because it needs real elapsed time (sleep),
# which would slow down/flake a 200-run batch. Known gap for the spike;
# add a mocked-time TTL test later if TTL correctness matters for results.
CUSTOM_HARNESS = {
    "lru-ttl-cache": '''
cache = LRUTTLCache(2)
cache.put("a", 1, 100)
cache.put("b", 2, 100)
results = []
results.append(cache.get("a") == 1)
cache.put("c", 3, 100)  # capacity 2, "a" just used via get, "b" is LRU -> evicted
results.append(cache.get("b") is None)
results.append(cache.get("a") == 1)
results.append(cache.get("c") == 3)
passed = sum(results)
total = len(results)
print(f"PASSED {passed}/{total}")
''',
}
