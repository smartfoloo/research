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

    # Bonus/exploratory tasks (2026-09-08) -- see prompts-bonus.md. All cases
    # hand-traced against the task prose below; none copied from a model
    # output. death-case assumption, stated explicitly since the prompt
    # doesn't say what to return on death: final_snake is the last snake
    # state before the fatal move (the move that would kill it is never
    # applied), matching "no further moves should be worked out."
    "simulate-snake": {
        "function": "simulate_snake",
        "cases": [
            # Given example: eats the only food on move 1 (grows, tail kept),
            # then a normal non-growing move.
            {"args": [(5, 5), [(2, 2), (1, 2)], [(3, 2)], ["RIGHT", "RIGHT"]],
             "expected": ([(4, 2), (3, 2), (2, 2)], True, 1)},
            # Two food items eaten in sequence -- food_eaten counts both and
            # the snake grows on each.
            {"args": [(5, 5), [(1, 0), (0, 0)], [(2, 0), (4, 0)], ["RIGHT", "RIGHT", "RIGHT"]],
             "expected": ([(4, 0), (3, 0), (2, 0), (1, 0)], True, 2)},
            # Wall death on move 2 -- final_snake is the state after move 1,
            # move 2 (which would leave the board) is never applied.
            {"args": [(3, 3), [(1, 1), (2, 1)], [], ["LEFT", "LEFT"]],
             "expected": ([(0, 1), (1, 1)], False, 0)},
            # Head moves onto the current tail cell, but the tail moves away
            # this same turn (no growth) -- explicitly not a collision.
            {"args": [(5, 5), [(2, 2), (2, 1), (1, 1), (1, 2)], [], ["LEFT"]],
             "expected": ([(1, 2), (2, 2), (2, 1), (1, 1)], True, 0)},
            # Head moves onto a non-tail body segment -- real collision,
            # dies immediately on move 1, final_snake is the original snake.
            {"args": [(5, 5), [(2, 2), (2, 3), (1, 3), (1, 2), (1, 1)], [], ["LEFT"]],
             "expected": ([(2, 2), (2, 3), (1, 3), (1, 2), (1, 1)], False, 0)},
            # Attempted reversal (opposite of current RIGHT direction) is
            # ignored -- snake just continues RIGHT instead of dying/turning.
            {"args": [(5, 5), [(2, 2), (1, 2)], [], ["LEFT"]],
             "expected": ([(3, 2), (2, 2)], True, 0)},
        ],
    },

    "apply-rewrite-rules": {
        "function": "apply_rewrite_rules",
        "cases": [
            # Given example.
            {"args": [[{"match_type": "path_prefix", "match_value": "/old-api/",
                        "action": "strip_prefix", "action_value": "/old-api"}],
                       ["http://api.example.com/old-api/users"]],
             "expected": ["http://api.example.com/users"]},
            # strip_prefix empties the path -- must fall back to "/".
            {"args": [[{"match_type": "path_prefix", "match_value": "/api",
                        "action": "strip_prefix", "action_value": "/api"}],
                       ["http://x.com/api"]],
             "expected": ["http://x.com/"]},
            # host exact match + redirect_host, scheme/path/query preserved.
            {"args": [[{"match_type": "host", "match_value": "old.example.com",
                        "action": "redirect_host", "action_value": "new.example.com"}],
                       ["http://old.example.com/path?q=1"]],
             "expected": ["http://new.example.com/path?q=1"]},
            # Wildcard subdomain matches a strict subdomain but NOT the bare
            # domain itself (explicitly excluded by the spec).
            {"args": [[{"match_type": "host", "match_value": "*.example.com",
                        "action": "redirect_host", "action_value": "cdn.example.com"}],
                       ["http://api.example.com/x", "http://example.com/x"]],
             "expected": ["http://cdn.example.com/x", "http://example.com/x"]},
            # query_param match + add_query_param appends to the existing query.
            {"args": [[{"match_type": "query_param", "match_value": "utm_source",
                        "action": "add_query_param", "action_value": "tag=abc"}],
                       ["http://x.com/p?utm_source=foo"]],
             "expected": ["http://x.com/p?utm_source=foo&tag=abc"]},
            # No rule matches -- unchanged.
            {"args": [[{"match_type": "path_prefix", "match_value": "/admin",
                        "action": "block"}],
                       ["http://x.com/public"]],
             "expected": ["http://x.com/public"]},
            # block action -- None instead of a rewritten URL.
            {"args": [[{"match_type": "path_prefix", "match_value": "/admin",
                        "action": "block"}],
                       ["http://x.com/admin/secret"]],
             "expected": [None]},
            # Rule priority: first matching rule wins even though a later
            # rule would also match -- stop after applying the first.
            {"args": [[{"match_type": "path_prefix", "match_value": "/api", "action": "block"},
                       {"match_type": "host", "match_value": "x.com",
                        "action": "redirect_host", "action_value": "y.com"}],
                       ["http://x.com/api/foo"]],
             "expected": [None]},
        ],
    },
}

# No CUSTOM_HARNESS needed — lru-ttl-cache (the only stateful task) was cut
# from the 6-task set.
CUSTOM_HARNESS = {}
