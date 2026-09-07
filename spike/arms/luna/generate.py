"""
Self-contained generation runner for the OpenAI gpt-5.6-luna arm.

Uses the Responses API (not Chat Completions) -- required for reasoning.effort
control and reasoning summaries on this model family. Separate provider,
separate schema, separate output dir -- zero overlap with the other three arms.

Settings, deliberately fixed and logged per generation (not left implicit --
see CLAUDE.md's Open Decisions note on the local/Gemini arms not doing this
from the start):
  - reasoning.effort = "medium" (provider default, explicit)
  - reasoning.summary = "auto" (abbreviated reasoning summary text, NOT the
    real chain-of-thought -- OpenAI does not expose that for this model
    family, confirmed 2026-09-07. This is weaker than qwen3.5/Gemma's full
    trace but still real, checkable text -- worth capturing regardless.)
  - temperature = 1
  - seed = 42 (best-effort determinism; OpenAI echoes back which fingerprint
    actually served the request)
  - max_output_tokens = 8000 (generous cap -- avoids repeating the exact
    truncation bug that silently cut off 61% of qwen3.5's ja_directive
    generations early in this project)

Response parsing is defensive on purpose: this is real billed usage (project
API key, not a free tier), and the exact Responses API JSON shape for this
specific model was not independently confirmed against a live call before
writing this script. Every raw response is saved verbatim regardless of
whether parsing succeeds, so nothing is lost if a field name is wrong --
worst case is an easy post-hoc fix, not lost data or wasted spend.

Usage:
  python spike/arms/luna/generate.py

Requires spike/.openai_api_key (gitignored, one line, no newline) or the
OPENAI_API_KEY environment variable. Start with SAMPLES_PER_CELL = 1 (a
24-call pilot: 6 tasks x 4 conditions) to check real cost/behavior before
raising it -- do not raise this without deliberately deciding to.
"""

import json
import time
import requests
from pathlib import Path

MODEL = "gpt-5.6-luna"
API_URL = "https://api.openai.com/v1/responses"

CONDITIONS = ["en_human", "ja_raw", "ja_directive", "mt_en"]
SAMPLES_PER_CELL = 6  # pilot (N=1, 24 calls, $0.0153) validated clean: 0
# failures after the seed-param fix, real cost matched prediction, reasoning
# summaries came back populated and language-taggable. Matching the other
# three arms' N=6 now.

REASONING_EFFORT = "medium"
REASONING_SUMMARY = "auto"
TEMPERATURE = 1
SEED = None  # Responses API rejected "seed" for this model with HTTP 400
# "Unknown parameter" on the first real attempt (2026-09-07) -- not supported
# here, unlike Chat Completions on other model families. Dropped rather than
# guessing at a different param name; system_fingerprint below is also gone
# for the same reason, so no determinism knob or fingerprint is available
# for this arm -- log that as a real limitation, don't fake one.
MAX_OUTPUT_TOKENS = 8000

MIN_SECONDS_BETWEEN_REQUESTS = 1.5  # Tier 1 gives 500 RPM / 500K TPM --
# enormous headroom for 24-144 calls. This is politeness, not a real
# constraint, unlike Groq's 12s pacing.

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PROMPTS_FILE = ROOT / "spike" / "prompts.json"
OUT_DIR = ROOT / "data" / "raw" / "luna"
KEY_FILE = ROOT / "spike" / ".openai_api_key"


def load_api_key():
    import os
    env_key = os.environ.get("OPENAI_API_KEY")
    if env_key:
        return env_key.strip()
    if KEY_FILE.exists():
        return KEY_FILE.read_text(encoding="utf-8").strip()
    raise RuntimeError(
        f"No API key found. Set OPENAI_API_KEY env var or create {KEY_FILE}"
    )


def load_prompts():
    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.pop("_readme", None)
    return data


def out_path(task, condition, sample_idx):
    safe_model = MODEL.replace(":", "-").replace("/", "-")
    fname = f"{safe_model}__{task}__{condition}__sample{sample_idx}.json"
    return OUT_DIR / fname


class RateLimiter:
    def __init__(self):
        self.last_request_time = 0.0

    def wait_if_needed(self):
        since_last = time.time() - self.last_request_time
        if since_last < MIN_SECONDS_BETWEEN_REQUESTS:
            time.sleep(MIN_SECONDS_BETWEEN_REQUESTS - since_last)

    def record(self):
        self.last_request_time = time.time()


def generate(api_key, prompt, limiter, max_retries=3):
    limiter.wait_if_needed()

    body = {
        "model": MODEL,
        "input": prompt,
        "reasoning": {"effort": REASONING_EFFORT, "summary": REASONING_SUMMARY},
        "temperature": TEMPERATURE,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
    }
    if SEED is not None:
        body["seed"] = SEED
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    for attempt in range(max_retries):
        resp = requests.post(API_URL, json=body, headers=headers, timeout=180)
        if resp.status_code == 429:
            wait = 15 * (attempt + 1)
            print(f"  (429 rate limited -- waiting {wait}s, attempt {attempt+1}/{max_retries})")
            time.sleep(wait)
            continue
        if resp.status_code >= 500:
            wait = 10 * (attempt + 1)
            print(f"  ({resp.status_code} server error -- waiting {wait}s, attempt {attempt+1}/{max_retries})")
            time.sleep(wait)
            continue
        if not resp.ok:
            # Surface the exact rejection reason immediately -- this is real
            # billed usage, cheap failures should be loud and fast to fix.
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:2000]}")
        limiter.record()
        return resp.json()

    raise RuntimeError("Exceeded max retries")


def extract_texts(result):
    """Defensive parsing: the exact Responses API shape for this model was
    not independently verified against a live call before writing this
    script. Walks the "output" array looking for message text and reasoning
    summary text under a few plausible field-name variants, rather than
    assuming one exact shape and crashing. Always returns strings (possibly
    empty), never raises -- the raw response is saved regardless, so a
    parsing gap is a fixable annotation issue, not lost data."""
    final_text_parts = []
    reasoning_summary_parts = []

    for item in result.get("output", []):
        item_type = item.get("type")
        if item_type == "message":
            for c in item.get("content", []):
                if c.get("type") in ("output_text", "text"):
                    final_text_parts.append(c.get("text", ""))
        elif item_type == "reasoning":
            summary = item.get("summary")
            if isinstance(summary, str):
                reasoning_summary_parts.append(summary)
            elif isinstance(summary, list):
                for s in summary:
                    if isinstance(s, dict):
                        reasoning_summary_parts.append(s.get("text", s.get("content", "")))
                    elif isinstance(s, str):
                        reasoning_summary_parts.append(s)

    # Fallback: some SDKs surface a top-level convenience field.
    if not final_text_parts and result.get("output_text"):
        final_text_parts.append(result["output_text"])

    return "\n\n".join(final_text_parts), "\n\n".join(reasoning_summary_parts)


def extract_usage(result):
    """Same defensiveness as extract_texts -- reasoning_tokens has appeared
    both top-level and nested under output_tokens_details across different
    OpenAI model families historically, so check both."""
    usage = result.get("usage", {})
    reasoning_tokens = usage.get("reasoning_tokens")
    if reasoning_tokens is None:
        reasoning_tokens = usage.get("output_tokens_details", {}).get("reasoning_tokens")
    return {
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "reasoning_tokens": reasoning_tokens,
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    prompts = load_prompts()
    limiter = RateLimiter()

    total = len(prompts) * len(CONDITIONS) * SAMPLES_PER_CELL
    done = 0
    skipped_existing = 0
    failed = []

    for task, task_prompts in prompts.items():
        for condition in CONDITIONS:
            prompt_text = task_prompts.get(condition)
            for sample_idx in range(1, SAMPLES_PER_CELL + 1):
                done += 1
                label = f"[{done}/{total}] {task} | {condition} | sample{sample_idx}"

                if prompt_text is None:
                    print(f"{label} -- skip (no prompt yet)")
                    continue

                fpath = out_path(task, condition, sample_idx)
                if fpath.exists():
                    skipped_existing += 1
                    print(f"{label} -- skip (already done)")
                    continue

                try:
                    t0 = time.time()
                    result = generate(api_key, prompt_text, limiter)
                    elapsed = time.time() - t0
                    final_text, reasoning_summary = extract_texts(result)
                    usage = extract_usage(result)

                    record = {
                        "raw_api_response": result,
                        "final_text": final_text,
                        "reasoning_summary": reasoning_summary,
                        **usage,
                        "system_fingerprint": result.get("system_fingerprint"),
                        "_meta": {
                            "model": MODEL,
                            "provider": "openai",
                            "task": task,
                            "condition": condition,
                            "sample_idx": sample_idx,
                            "prompt_text": prompt_text,
                            "reasoning_effort": REASONING_EFFORT,
                            "reasoning_summary_setting": REASONING_SUMMARY,
                            "temperature": TEMPERATURE,
                            "seed": SEED,
                            "max_output_tokens": MAX_OUTPUT_TOKENS,
                            "elapsed_seconds": elapsed,
                            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        },
                    }
                    with open(fpath, "w", encoding="utf-8") as f:
                        json.dump(record, f, ensure_ascii=False, indent=2)
                    print(f"{label} -- ok ({elapsed:.1f}s, "
                          f"{usage.get('total_tokens')} tokens, "
                          f"{usage.get('reasoning_tokens')} reasoning)")
                except Exception as e:
                    failed.append(label)
                    print(f"{label} -- FAILED: {e}")

    print("\n--- run complete ---")
    print(f"total slots:            {total}")
    print(f"skipped (already done): {skipped_existing}")
    print(f"failed:                 {len(failed)}")
    if failed:
        print("failed runs:")
        for f in failed:
            print(f"  {f}")


if __name__ == "__main__":
    main()
