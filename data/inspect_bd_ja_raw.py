import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

for i in [1, 2, 3]:
    f = f"data/raw/qwen3.5-9b__business-days__ja_raw__sample{i}.grade.json"
    d = json.load(open(f, encoding="utf-8"))
    print("=" * 20, "sample", i, "pass:", d["passed_cases"], "/", d["total_cases"], "=" * 20)
    code = d["extracted_code"]
    has_holiday = "holiday" in code.lower() or "祝日" in code or "calendar" in code.lower()
    print("mentions holiday/calendar machinery:", has_holiday)
    print(code[:400])
    print("...")
    print()
