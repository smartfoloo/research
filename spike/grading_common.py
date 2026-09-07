"""
Shared grading utilities used by every arm's grade.py (qwen3_5_local, gemma,
flash_lite, groq_qwen3_8). Extracted from the original grade_generations.py
so a future fix to grading logic (extraction, harness-building, sandboxing)
applies to all four arms at once instead of needing to be copy-pasted.

Not runnable on its own -- each arm's grade.py imports from this module.
"""

import re
import subprocess
from pathlib import Path

from test_cases import TEST_CASES, CUSTOM_HARNESS

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
        "    # Tuple/list are graded as equivalent at every nesting depth: the",
        "    # prompts say 'returns (a, b)' or a list of (x, y) coordinate",
        "    # tuples in prose, not 'must return a Python tuple'. Recursive so",
        "    # a nested structure (e.g. a list of coordinate tuples) doesn't",
        "    # fail grading just because the model returned lists instead of",
        "    # tuples for the inner elements.",
        "    if isinstance(v, (list, tuple)):",
        "        return [_norm(x) for x in v]",
        "    return v",
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
