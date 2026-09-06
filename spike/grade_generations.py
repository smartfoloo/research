"""
Grades saved generations by running them in an isolated Docker container.

For each ungraded file in data/raw/*.json:
  1. Extract the Python code from the model's raw response text.
  2. Combine it with the task's test harness.
  3. Run it inside a Docker container: no network, memory-capped, timeout.
  4. Parse "PASSED X/Y" from stdout, save a .grade.json next to the raw file.

Usage:
  python grade_generations.py

Requires Docker running. Skips anything already graded — safe to re-run.
"""

import json
import re
import subprocess
import time
from pathlib import Path

from test_cases import TEST_CASES, CUSTOM_HARNESS

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"

DOCKER_IMAGE = "python:3.11-slim"
CONTAINER_TIMEOUT_SECONDS = 15  # wall-clock cap on the docker run itself


def extract_code(response_text: str) -> str:
    """Pull Python code out of a model response. Uses only the FIRST fenced
    ```python block (the model's primary answer). Models routinely show a
    revision, an alternative implementation, or a separate usage-demo
    snippet in later fenced blocks within the same response; joining all of
    them let a later, broken/incomplete block silently redefine a correct
    earlier function, or mixed indentation between blocks broke the syntax
    outright. Falls back to the first ``` fenced block of any kind, then to
    the whole response."""
    fenced_py = re.findall(r"```python\s*\n(.*?)```", response_text, re.DOTALL)
    if fenced_py:
        return fenced_py[0].strip()

    fenced_any = re.findall(r"```\s*\n?(.*?)```", response_text, re.DOTALL)
    if fenced_any:
        return fenced_any[0].strip()

    return response_text.strip()


def build_test_script(task: str, extracted_code: str) -> str:
    if task in CUSTOM_HARNESS:
        return extracted_code + "\n\n" + CUSTOM_HARNESS[task]

    spec = TEST_CASES[task]
    fn = spec["function"]
    # Models routinely append their own demo/example calls after the
    # function definition. If one of those hits a real bug in the model's
    # own code, it's a runtime exception that would otherwise kill the whole
    # script before our test cases below ever run. Isolate it: as long as
    # `fn` gets defined before the crash (the near-universal pattern), our
    # own test cases still execute normally afterward. This does NOT catch
    # syntax errors (those fail script compilation entirely, before any
    # execution) — those remain genuine failures.
    indented_code = "\n".join("    " + line for line in extracted_code.splitlines())
    lines = [
        "try:",
        indented_code,
        "except Exception as _submission_exc:",
        "    print('(non-fatal) submitted code raised at top level: '"
        " + repr(_submission_exc))",
        "",
        "def _norm(v):",
        "    # top-level tuple/list are graded as equivalent: the prompts say",
        "    # 'returns (a, b)' in prose, not 'must return a Python tuple'.",
        "    return list(v) if isinstance(v, tuple) else v",
        "",
        "passed = 0",
        f"total = {len(spec['cases'])}",
        "",
    ]
    for i, case in enumerate(spec["cases"]):
        args_repr = ", ".join(repr(a) for a in case["args"])
        if "expect_exception" in case:
            exc = case["expect_exception"]
            lines.append(f"try:")
            lines.append(f"    {fn}({args_repr})")
            lines.append(f"    print('FAIL case {i}: expected {exc}, no exception raised')")
            lines.append(f"except {exc}:")
            lines.append(f"    passed += 1")
            lines.append(f"except Exception as e:")
            lines.append(f"    print(f'FAIL case {i}: expected {exc}, got {{type(e).__name__}}')")
        else:
            expected_repr = repr(case["expected"])
            lines.append(f"try:")
            lines.append(f"    result = {fn}({args_repr})")
            lines.append(f"    if _norm(result) == _norm({expected_repr}):")
            lines.append(f"        passed += 1")
            lines.append(f"    else:")
            # Not an f-string template: expected_repr can itself contain the
            # same quote character used to delimit the template, which would
            # break the generated script's syntax whenever expected contains
            # a string (e.g. ['A', 'B']). repr() on the whole message
            # re-escapes it into a safe literal regardless of what's inside.
            fail_prefix = repr(f"FAIL case {i}: expected {expected_repr}, got ")
            lines.append(f"        print({fail_prefix} + repr(result))")
            lines.append(f"except Exception as e:")
            lines.append(f"    print(f'FAIL case {i}: raised {{type(e).__name__}}: {{e}}')")
        lines.append("")

    lines.append('print(f"PASSED {passed}/{total}")')
    return "\n".join(lines)


def run_in_docker(script_text: str, workdir: Path) -> tuple[str, str, int]:
    script_path = workdir / "test_script.py"
    script_path.write_text(script_text, encoding="utf-8")

    cmd = [
        "docker", "run", "--rm",
        "--network", "none",
        "--memory", "512m",
        "-v", f"{workdir}:/app",
        "-w", "/app",
        DOCKER_IMAGE,
        "python", "test_script.py",
    ]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True,
            # Windows defaults subprocess text-decoding to the system
            # codepage (cp1252 here), not UTF-8. Generated code can contain
            # non-ASCII (e.g. Japanese comments from JA-condition outputs),
            # which then crashes decoding entirely. Force UTF-8, matching
            # what the container itself actually writes.
            encoding="utf-8", errors="replace",
            timeout=CONTAINER_TIMEOUT_SECONDS,
        )
        return proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -1


def parse_pass_count(stdout: str):
    m = re.search(r"PASSED (\d+)/(\d+)", stdout)
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


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
        # take down the other 71 — record it as an error and keep going.
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

            import tempfile
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
