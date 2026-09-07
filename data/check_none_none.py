import json, glob, os

for f in sorted(glob.glob("data/raw/*.grade.json")):
    d = json.load(open(f, encoding="utf-8"))
    if d.get("passed_cases") is None:
        stderr = d.get("stderr", "")
        last_line = stderr.strip().splitlines()[-1] if stderr.strip() else "(empty stderr)"
        print(os.path.basename(f))
        print("  returncode:", d.get("docker_returncode"), "| last stderr line:", last_line)
