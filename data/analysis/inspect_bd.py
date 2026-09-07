import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

for i in [1, 2, 3]:
    f = f"data/raw/qwen3_5_local/qwen3.5-9b__business-days__en_human__sample{i}.grade.json"
    d = json.load(open(f, encoding="utf-8"))
    print("=" * 20, "sample", i, "=" * 20)
    print(d["extracted_code"])
    print()
