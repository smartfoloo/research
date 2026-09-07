"""
Grades local qwen3.5:9b generations (data/raw/qwen3_5_local/*.json) by
running them in an isolated Docker container.

For each ungraded file:
  1. Extract the Python code from the model's raw response text.
  2. Combine it with the task's test harness.
  3. Run it inside a Docker container: no network, memory-capped, timeout.
  4. Parse "PASSED X/Y" from stdout, save a .grade.json next to the raw file.

Extraction/harness/sandbox logic lives in spike/grading_common.py, shared
with the other three arms.

Usage (from anywhere):
  python spike/arms/qwen3_5_local/grade.py

Requires Docker running. Skips anything already graded — safe to re-run.
"""

import json
import sys
import time
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))  # spike/
from grading_common import extract_code, build_test_script, run_in_docker, parse_pass_count

ROOT = Path(__file__).resolve().parent.parent.parent.parent
RAW_DIR = ROOT / "data" / "raw" / "qwen3_5_local"


def main():
    raw_files = sorted(RAW_DIR.glob("*.json"))
    raw_files = [f for f in raw_files if not f.name.endswith(".grade.json")]

    graded = 0
    skipped = 0
    errors = []

    for raw_file in raw_files:
        # NOT raw_file.with_suffix(...).with_suffix(...): model names like
        # "qwen3.5-9b" contain their own dot, which pathlib's with_suffix
        # mistakes for a suffix boundary once ".json" is stripped, collapsing
        # every filename to the same "qwen3.grade.json". Plain string
        # suffix-stripping avoids that.
        grade_file = raw_file.with_name(raw_file.name[: -len(".json")] + ".grade.json")
        if grade_file.exists():
            skipped += 1
            continue

        # One bad file (crash in extraction, docker, or parsing) must not
        # take down the other 143 — record it as an error and keep going.
        try:
            with open(raw_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            task = data["_meta"]["task"]
            response_text = data.get("response", "")
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
                "condition": data["_meta"]["condition"],
                "sample_idx": data["_meta"]["sample_idx"],
                "extracted_code": extracted,
                "stdout": stdout,
                "stderr": stderr,
                "docker_returncode": returncode,
                "passed_cases": passed,
                "total_cases": total,
                "all_passed": (passed == total) if passed is not None else False,
                "prompt_eval_count": data.get("prompt_eval_count"),
                "eval_count": data.get("eval_count"),
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
