import json, glob
from collections import defaultdict

order = ["en_human", "ja_raw", "ja_directive", "mt_en"]


def compute(pattern, token_field_fn, label):
    by_cond = defaultdict(lambda: {"n": 0, "correct": 0, "total_tokens": 0})
    for f in sorted(glob.glob(pattern)):
        d = json.load(open(f, encoding="utf-8"))
        cond = d["condition"]
        b = by_cond[cond]
        b["n"] += 1
        if d["all_passed"]:
            b["correct"] += 1
        b["total_tokens"] += token_field_fn(d)

    print(f"=== {label} ===")
    print(f"{'condition':14s}{'n':>4s}{'correct':>8s}{'pass%':>7s}{'total_tok':>11s}{'tok/correct':>13s}")
    for c in order:
        b = by_cond[c]
        pass_rate = 100 * b["correct"] / b["n"] if b["n"] else 0
        tok_per_correct = b["total_tokens"] / b["correct"] if b["correct"] else float("inf")
        tpc_str = f"{tok_per_correct:.0f}" if b["correct"] else "inf (0 correct)"
        print(f"{c:14s}{b['n']:4d}{b['correct']:8d}{pass_rate:6.0f}%{b['total_tokens']:11d}{tpc_str:>13s}")
    print()
    return by_cond


qwen_data = compute(
    "data/raw/*.grade.json",
    lambda d: (d.get("prompt_eval_count") or 0) + (d.get("eval_count") or 0),
    "qwen3.5:9b (local, N=6/cell, 36 samples/condition)",
)

gemma_data = compute(
    "data/raw_gemma/*.grade.json",
    lambda d: d.get("total_token_count") or 0,
    "gemma-4-31b-it (API, N=6/cell, 36 samples/condition)",
)

print("=== Combined: tokens per CORRECT solution, both models ===")
print(f"{'condition':14s}{'qwen3.5':>12s}{'gemma-4-31b':>14s}")
for c in order:
    q = qwen_data[c]
    g = gemma_data[c]
    q_val = q["total_tokens"] / q["correct"] if q["correct"] else None
    g_val = g["total_tokens"] / g["correct"] if g["correct"] else None
    q_str = f"{q_val:.0f}" if q_val else "N/A"
    g_str = f"{g_val:.0f}" if g_val else "N/A"
    print(f"{c:14s}{q_str:>12s}{g_str:>14s}")
