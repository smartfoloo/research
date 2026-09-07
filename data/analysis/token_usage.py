import json, glob
from collections import defaultdict

by_cond = defaultdict(lambda: {"n": 0, "prompt": 0, "eval": 0})
by_task_cond = defaultdict(lambda: {"n": 0, "prompt": 0, "eval": 0})

for f in sorted(glob.glob("data/raw/qwen3_5_local/*.json")):
    if f.endswith(".grade.json"):
        continue
    d = json.load(open(f, encoding="utf-8"))
    task = d["_meta"]["task"]
    if task == "business-days":
        continue  # being regenerated under new wording, exclude for now
    cond = d["_meta"]["condition"]
    pe = d.get("prompt_eval_count") or 0
    ev = d.get("eval_count") or 0

    for bucket in (by_cond[cond], by_task_cond[(task, cond)]):
        bucket["n"] += 1
        bucket["prompt"] += pe
        bucket["eval"] += ev

order = ["en_human", "ja_raw", "ja_directive", "mt_en"]

print("NOTE: Ollama's eval_count is TOTAL output tokens (thinking + final")
print("answer bundled together) -- it does not separate reasoning-trace")
print("tokens from response tokens. prompt_eval_count is input tokens.\n")

print("=== By condition (excludes business-days, currently regenerating) ===")
print(f"{'condition':14s}{'n':>4s}{'avg_input':>12s}{'avg_output':>12s}{'avg_total':>12s}")
for c in order:
    b = by_cond[c]
    if b["n"] == 0:
        continue
    avg_in = b["prompt"] / b["n"]
    avg_out = b["eval"] / b["n"]
    print(f"{c:14s}{b['n']:4d}{avg_in:12.0f}{avg_out:12.0f}{avg_in+avg_out:12.0f}")

tasks = ["currency-format", "reverse-list-elements", "eval-expression",
         "shortest-path", "bank-rollback"]
print("\n=== avg output (eval_count) tokens by task x condition ===")
header = "task".ljust(24) + "".join(c.ljust(14) for c in order)
print(header)
for t in tasks:
    row = t.ljust(24)
    for c in order:
        b = by_task_cond[(t, c)]
        avg_out = b["eval"] / b["n"] if b["n"] else 0
        row += f"{avg_out:.0f} (n={b['n']})".ljust(14)
    print(row)
