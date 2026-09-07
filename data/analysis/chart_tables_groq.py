import json, glob
from collections import defaultdict

order = ["en_human", "ja_raw", "ja_directive", "mt_en"]

by_cond = defaultdict(lambda: {"n": 0, "correct": 0, "total_tokens": 0})
for f in sorted(glob.glob("data/raw/groq_qwen3_8/*.grade.json")):
    d = json.load(open(f, encoding="utf-8"))
    cond = d["condition"]
    b = by_cond[cond]
    b["n"] += 1
    if d["all_passed"]:
        b["correct"] += 1
    b["total_tokens"] += d.get("total_tokens") or 0

print("=== CHART 1: avg tokens/generation, indexed to en_human ===")
base = by_cond["en_human"]["total_tokens"] / by_cond["en_human"]["n"]
print(f"{'condition':14s}{'avg_tokens':>12s}{'ratio':>8s}")
for c in order:
    b = by_cond[c]
    avg = b["total_tokens"] / b["n"]
    print(f"{c:14s}{avg:12.0f}{avg/base:8.2f}")

print()
print("=== CHART 2: tokens per correct solution ===")
print(f"{'condition':14s}{'pass%':>7s}{'tok/correct':>13s}")
for c in order:
    b = by_cond[c]
    pr = 100 * b["correct"] / b["n"]
    tpc = b["total_tokens"] / b["correct"] if b["correct"] else None
    tpc_str = f"{tpc:.0f}" if tpc else "N/A"
    print(f"{c:14s}{pr:6.0f}%{tpc_str:>13s}")
