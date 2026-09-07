import json, glob, os

truncated = []
for f in sorted(glob.glob("data/raw/qwen3_5_local/*.json")):
    if f.endswith(".grade.json"):
        continue
    d = json.load(open(f, encoding="utf-8"))
    if d.get("done_reason") == "length":
        truncated.append(f)

for f in truncated:
    os.remove(f)
print(f"removed {len(truncated)} truncated raw generations (will regenerate)")

grade_files = glob.glob("data/raw/qwen3_5_local/*.grade.json")
for f in grade_files:
    os.remove(f)
print(f"removed {len(grade_files)} grade files (will regrade everything fresh)")
