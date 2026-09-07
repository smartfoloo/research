"""
Grades Groq / qwen-3.8-27b generations (data/raw/groq_qwen3_8/*.json).

Same structure as the other three arms' grade.py. response_text is already
the full final answer (no thought-part filtering needed -- this model
returns plain message.content, no reasoning trace, confirmed at generation
time). Reuses extract_code/build_test_script/run_in_docker/parse_pass_count
from spike/grading_common.py.

Usage (from anywhere):
  python spike/arms/groq_qwen3_8/grade.py

Requires Docker running. Skips anything already graded -- safe to re-run.
"""

import json
import sys
import time
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))  # spike/
from grading_common import extract_code, build_test_script, run_in_docker, parse_pass_count

ROOT = Path(__file__).resolve().parent.parent.parent.parent
RAW_DIR = ROOT / "data" / "raw" / "groq_qwen3_8"


def main():
    raw_files = sorted(RAW_DIR.glob("*.json"))
    raw_files = [f for f in raw_files if not f.name.endswith(".grade.json")]

    graded = 0
    skipped = 0
    errors = []

    for raw_file in raw_files:
        grade_file = raw_file.with_name(raw_file.name[: -len(".json")] + ".grade.json")
        if grade_file.exists():
            skipped += 1
            continue

        try:
            with open(raw_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            task = data["_meta"]["task"]
            response_text = data.get("response_text", "")
            extracted = extract_code(response_text)

            if not extracted:
                errors.append((raw_file.name, "no code extracted"))
                continue

            test_script = build_test_script(task, extracted)

            with tempfile.TemporaryDirectory() as tmpdir:
                stdout, stderr, returncode = run_in_docker(test_script, Path(tmpdir))

            passed, total = parse_pass_count(stdout)

            result = {
                "raw_file": raw_file.name,
                "task": task,
                "model": data["_meta"]["model"],
                "provider": data["_meta"].get("provider"),
                "condition": data["_meta"]["condition"],
                "sample_idx": data["_meta"]["sample_idx"],
                "extracted_code": extracted,
                "stdout": stdout,
                "stderr": stderr,
                "docker_returncode": returncode,
                "passed_cases": passed,
                "total_cases": total,
                "all_passed": (passed == total) if passed is not None else False,
                "prompt_tokens": data.get("prompt_tokens"),
                "completion_tokens": data.get("completion_tokens"),
                "total_tokens": data.get("total_tokens"),
                "groq_seed": data.get("groq_seed"),
                "graded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }

            with open(grade_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            errors.append((raw_file.name, f"{type(e).__name__}: {e}"))
            continue

        status = "PASS" if result["all_passed"] else "FAIL"
        print(f"{raw_file.name}: {status} ({passed}/{total})")
        graded += 1

    print(f"\ngraded: {graded}, already done: {skipped}, errors: {len(errors)}")
    for name, msg in errors:
        print(f"  ERROR {name}: {msg}")


if __name__ == "__main__":
    main()
