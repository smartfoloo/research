import json, sys, io, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

tasks = ["business-days", "currency-format", "reverse-list-elements",
         "eval-expression", "shortest-path", "bank-rollback"]

for task in tasks:
    for i in [1, 2, 3]:
        f = f"data/raw/qwen3.5-9b__{task}__en_human__sample{i}.grade.json"
        d = json.load(open(f, encoding="utf-8"))
        if d["all_passed"]:
            continue
        print("=" * 30)
        print(f"{task} sample{i}: {d['passed_cases']}/{d['total_cases']}")
        stdout = d["stdout"].strip()
        if stdout:
            print("--- stdout ---")
            print(stdout)
        else:
            print("--- stderr (last 3 lines) ---")
            print("\n".join(d["stderr"].strip().splitlines()[-3:]))
        print()
