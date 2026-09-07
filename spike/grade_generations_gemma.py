"""
Grades Gemma / Google AI Studio generations (data/raw_gemma/*.json).

Separate from grade_generations.py because the raw JSON schema differs from
Ollama's: Gemini returns candidates[].content.parts[], where reasoning parts
are flagged "thought": true, rather than Ollama's flat "response" string.
run_generations_gemma.py already split this out at generation time into
"final_text" (non-thought parts) and "thinking_text" (thought parts) -- this
script picks up from "final_text".

Everything AFTER "get the final answer text" is identical to the local arm --
same extract_code() (first fenced ```python block only), same
build_test_script() (same TEST_CASES, same tuple/list normalization, same
top-level-crash isolation), same Docker sandboxing. Reused directly from
grade_generations.py rather than duplicated, so a future fix to grading
logic applies to both arms at once.

Usage:
  python grade_generations_gemma.py

Requires Docker running. Skips anything already graded -- safe to re-run.
"""

import json
import time
import tempfile
from pathlib import Path

from grade_generations import extract_code, build_test_script, run_in_docker, parse_pass_count

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw_gemma"


def main():
    raw_files = sorted(RAW_DIR.glob("*.json"))
    raw_files = [f for f in raw_files if not f.name.endswith(".grade.json")]

    graded = 0
    skipped = 0
    errors = []

    for raw_file in raw_files:
        # Plain string suffix-stripping, not pathlib with_suffix chaining --
        # model names with their own dots (not an issue for "gemma-4-31b-it"
        # specifically, but keeping this consistent with the local-arm fix
        # avoids reintroducing that exact bug class here).
        grade_file = raw_file.with_name(raw_file.name[: -len(".json")] + ".grade.json")
        if grade_file.exists():
            skipped += 1
            continue

        try:
            with open(raw_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            task = data["_meta"]["task"]
            final_text = data.get("final_text", "")
            extracted = extract_code(final_text)

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
                "prompt_token_count": data.get("prompt_token_count"),
                "candidates_token_count": data.get("candidates_token_count"),
                "thoughts_token_count": data.get("thoughts_token_count"),
                "total_token_count": data.get("total_token_count"),
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
