"""
Test cases per task. VERIFY THESE BY HAND before trusting grading results —
a wrong expected value silently fails every correct implementation.

Standard tasks: function_name(*args) is called, result compared to
`expected` with ==, unless `expect_exception` is set (exception class name
as a string), in which case the call must raise that exception type.

Reduced to 6 tasks (2026-09-05) to match prompts-en.md for the 2-day
deadline. Full 10-task versions removed here; task-specs-en.md still has
the full set documented if useful for the later full study.
"""

TEST_CASES = {
    "business-days": {
        "function": "business_days",
        "cases": [
            {"args": ["2024-01-01", "2024-01-08"], "expected": 4},
            {"args": ["2024-01-01", "2024-01-01"], "expected": 0},
            {"args": ["2024-01-06", "2024-01-08"], "expected": 0},
            {"args": ["2024-01-01", "2024-01-02"], "expected": 0},
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
}

# No CUSTOM_HARNESS needed — lru-ttl-cache (the only stateful task) was cut
# from the 6-task set.
CUSTOM_HARNESS = {}
