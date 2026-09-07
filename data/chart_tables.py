import json, glob
from collections import defaultdict

order = ["en_human", "ja_raw", "ja_directive", "mt_en"]


def totals(pattern, token_field_fn):
    by_cond = defaultdict(lambda: {"n": 0, "correct": 0, "total_tokens": 0})
    for f in sorted(glob.glob(pattern)):
        d = json.load(open(f, encoding="utf-8"))
        cond = d["condition"]
        b = by_cond[cond]
        b["n"] += 1
        if d["all_passed"]:
            b["correct"] += 1
        b["total_tokens"] += token_field_fn(d)
    return by_cond


qwen = totals("data/raw/*.grade.json", lambda d: (d.get("prompt_eval_count") or 0) + (d.get("eval_count") or 0))
gemma = totals("data/raw_gemma/*.grade.json", lambda d: d.get("total_token_count") or 0)

print("=== CHART 1 TABLE: avg tokens/generation, indexed to each model's own en_human ===")
print("condition,qwen3.5_avg_tokens,qwen3.5_ratio,gemma_avg_tokens,gemma_ratio")
q_base = qwen["en_human"]["total_tokens"] / qwen["en_human"]["n"]
g_base = gemma["en_human"]["total_tokens"] / gemma["en_human"]["n"]
for c in order:
    q_avg = qwen[c]["total_tokens"] / qwen[c]["n"]
    g_avg = gemma[c]["total_tokens"] / gemma[c]["n"]
    print(f"{c},{q_avg:.0f},{q_avg/q_base:.2f},{g_avg:.0f},{g_avg/g_base:.2f}")

print()
print("=== CHART 2 TABLE: tokens per correct solution ===")
print("condition,qwen3.5_pass_rate,qwen3.5_tokens_per_correct,gemma_pass_rate,gemma_tokens_per_correct")
for c in order:
    q, g = qwen[c], gemma[c]
    q_pr = 100 * q["correct"] / q["n"]
    g_pr = 100 * g["correct"] / g["n"]
    q_tpc = q["total_tokens"] / q["correct"] if q["correct"] else None
    g_tpc = g["total_tokens"] / g["correct"] if g["correct"] else None
    print(f"{c},{q_pr:.0f}%,{q_tpc:.0f},{g_pr:.0f}%,{g_tpc:.0f}")
