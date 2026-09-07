import json, glob, os

trunc = []
for f in sorted(glob.glob("data/raw/*.json")):
    if f.endswith(".grade.json"):
        continue
    d = json.load(open(f, encoding="utf-8"))
    if d.get("done_reason") == "length":
        trunc.append(os.path.basename(f))

print(f"total truncated (done_reason=length): {len(trunc)} / 72")
for name in trunc:
    print(" ", name)

# breakdown by condition
from collections import Counter
cond_counts = Counter(n.split("__")[2] for n in trunc)
print("\nby condition:", dict(cond_counts))
