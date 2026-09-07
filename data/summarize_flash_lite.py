import json, glob
from collections import defaultdict

by_cond = defaultdict(lambda: [0, 0])
by_task_cond = defaultdict(lambda: [0, 0])
tok_by_cond = defaultdict(lambda: {"n": 0, "total": 0})

for f in sorted(glob.glob("data/raw_flash_lite/*.grade.json")):
    d = json.load(open(f, encoding="utf-8"))
    cond = d["condition"]
    task = d["task"]
    by_cond[cond][1] += 1
    by_task_cond[(task, cond)][1] += 1
    if d["all_passed"]:
        by_cond[cond][0] += 1
        by_task_cond[(task, cond)][0] += 1
    tb = tok_by_cond[cond]
    tb["n"] += 1
    tb["total"] += d.get("total_token_count") or 0

order = ["en_human", "ja_raw", "ja_directive", "mt_en"]
print("=== gemini-3.5-flash-lite: overall pass rate by condition (36 samples each) ===")
for c in order:
    p, n = by_cond[c]
    print(f"  {c:14s} {p}/{n}  ({100*p/n:.0f}%)")

tasks = ["business-days", "currency-format", "reverse-list-elements",
         "eval-expression", "shortest-path", "bank-rollback"]
print("\n=== Per task x condition (6 samples each) ===")
header = "task".ljust(24) + "".join(c.ljust(14) for c in order)
print(header)
for t in tasks:
    row = t.ljust(24)
    for c in order:
        p, n = by_task_cond[(t, c)]
        row += f"{p}/{n}".ljust(14)
    print(row)

print("\n=== avg total tokens/generation by condition ===")
for c in order:
    tb = tok_by_cond[c]
    print(f"  {c:14s} {tb['total']/tb['n']:.0f}")
