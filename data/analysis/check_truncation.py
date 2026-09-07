import json, glob, os

for f in sorted(glob.glob("data/raw/qwen3_5_local/*.json")):
    if f.endswith(".grade.json"):
        continue
    d = json.load(open(f, encoding="utf-8"))
    if not d.get("response"):
        pe, e = d.get("prompt_eval_count"), d.get("eval_count")
        total = (pe or 0) + (e or 0)
        print(os.path.basename(f), "done_reason=", d.get("done_reason"), "prompt=", pe, "eval=", e, "total=", total)
