import json, glob, os

removed = 0
for f in glob.glob("data/raw/*.grade.json"):
    d = json.load(open(f, encoding="utf-8"))
    if d.get("passed_cases") is None:
        os.remove(f)
        removed += 1
        print("removed stale crash grade:", os.path.basename(f))
print("total removed:", removed)
