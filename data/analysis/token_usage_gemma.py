import json, glob
from collections import defaultdict

by_cond = defaultdict(lambda: {"n": 0, "prompt": 0, "candidates": 0, "thoughts": 0, "total": 0})
by_task_cond = defaultdict(lambda: {"n": 0, "total": 0})

for f in sorted(glob.glob("data/raw/gemma/*.grade.json")):
    d = json.load(open(f, encoding="utf-8"))
    cond = d["condition"]
    task = d["task"]
    pt = d.get("prompt_token_count") or 0
    ct = d.get("candidates_token_count") or 0
    tt = d.get("thoughts_token_count") or 0
    tot = d.get("total_token_count") or 0

    b = by_cond[cond]
    b["n"] += 1
    b["prompt"] += pt
    b["candidates"] += ct
    b["thoughts"] += tt
    b["total"] += tot

    bt = by_task_cond[(task, cond)]
    bt["n"] += 1
    bt["total"] += tot

order = ["en_human", "ja_raw", "ja_directive", "mt_en"]
print("=== Gemma 4 31B IT: avg tokens per generation by condition (n=36 each) ===")
print(f"{'condition':14s}{'avg_prompt':>12s}{'avg_thoughts':>14s}{'avg_answer':>12s}{'avg_total':>12s}")
for c in order:
    b = by_cond[c]
    n = b["n"]
    print(f"{c:14s}{b['prompt']/n:12.0f}{b['thoughts']/n:14.0f}{b['candidates']/n:12.0f}{b['total']/n:12.0f}")

tasks = ["business-days", "currency-format", "reverse-list-elements",
         "eval-expression", "shortest-path", "bank-rollback"]
print("\n=== avg TOTAL tokens by task x condition ===")
header = "task".ljust(24) + "".join(c.ljust(14) for c in order)
print(header)
for t in tasks:
    row = t.ljust(24)
    for c in order:
        b = by_task_cond[(t, c)]
        avg = b["total"] / b["n"] if b["n"] else 0
        row += f"{avg:.0f}".ljust(14)
    print(row)
