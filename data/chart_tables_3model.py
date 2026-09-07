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
flite = totals("data/raw_flash_lite/*.grade.json", lambda d: d.get("total_token_count") or 0)

models = [("qwen3.5", qwen), ("gemma-4-31b", gemma), ("flash-lite", flite)]

print("=== CHART 1: avg tokens/generation, indexed to each model's own en_human ===")
header = "condition".ljust(14)
for name, _ in models:
    header += f"{name}_avg".rjust(14) + f"{name}_ratio".rjust(14)
print(header)
bases = {name: data["en_human"]["total_tokens"] / data["en_human"]["n"] for name, data in models}
for c in order:
    row = c.ljust(14)
    for name, data in models:
        avg = data[c]["total_tokens"] / data[c]["n"]
        row += f"{avg:.0f}".rjust(14) + f"{avg/bases[name]:.2f}".rjust(14)
    print(row)

print()
print("=== CHART 2: tokens per correct solution ===")
header = "condition".ljust(14)
for name, _ in models:
    header += f"{name}_pass%".rjust(12) + f"{name}_tok/correct".rjust(18)
print(header)
for c in order:
    row = c.ljust(14)
    for name, data in models:
        b = data[c]
        pr = 100 * b["correct"] / b["n"]
        tpc = b["total_tokens"] / b["correct"] if b["correct"] else None
        tpc_str = f"{tpc:.0f}" if tpc else "N/A"
        row += f"{pr:.0f}%".rjust(12) + tpc_str.rjust(18)
    print(row)
