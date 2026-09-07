import json, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

files = [
    "data/raw/qwen3_5_local/qwen3.5-9b__business-days__en_human__sample1.grade.json",
    "data/raw/qwen3_5_local/qwen3.5-9b__bank-rollback__ja_directive__sample2.grade.json",
    "data/raw/qwen3_5_local/qwen3.5-9b__currency-format__en_human__sample3.grade.json",
    "data/raw/qwen3_5_local/qwen3.5-9b__shortest-path__ja_raw__sample1.grade.json",
]

for fp in files:
    d = json.load(open(fp, encoding="utf-8"))
    print("=" * 20, fp, "=" * 20)
    code = d["extracted_code"]
    print(code[-600:])
    print()
