"""
Self-contained generation runner for the Gemma / Google AI Studio arm.

Completely separate from the qwen3_5_local arm's generate.py -- different
provider, different API shape, different rate limits, different output
directory. Nothing here touches the local-arm data or code path.

Reuses spike/prompts.json (same tasks/conditions as the local arm) so the
two arms stay directly comparable.

Usage (from anywhere):
  python spike/arms/gemma/generate.py

Requires spike/.gemma_api_key to exist (gitignored, one line, no newline) --
or set the GEMMA_API_KEY environment variable instead.

Free tier limits as given: 30 RPM, 16,000 TPM, 14,400 RPD. This script
enforces a minimum gap between requests and a rolling 60s token-usage window
to stay under both, using each call's ACTUAL reported usage (not an
estimate) to decide whether to wait before the next call.
"""

import json
import time
import requests
from pathlib import Path

MODEL = "gemma-4-31b-it"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

CONDITIONS = ["en_human", "ja_raw", "ja_directive", "mt_en"]
SAMPLES_PER_CELL = 6  # pilot (N=1, 24 calls) validated clean: 0 failures, no
# rate-limit hits, good usage metadata. Matching the local arm's N=6 now.

# Free-tier limits: 30 RPM, 16,000 TPM, 14,400 RPD. Leave real margin since
# these are hard caps on someone else's free tier, not ours to push against.
MIN_SECONDS_BETWEEN_REQUESTS = 3.0
TPM_SAFETY_CAP = 12000  # stay under 16000 with margin
ROLLING_WINDOW_SECONDS = 60

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PROMPTS_FILE = ROOT / "spike" / "prompts.json"
OUT_DIR = ROOT / "data" / "raw" / "gemma"
KEY_FILE = ROOT / "spike" / ".gemma_api_key"


def load_api_key():
    import os
    env_key = os.environ.get("GEMMA_API_KEY")
    if env_key:
        return env_key.strip()
    if KEY_FILE.exists():
        return KEY_FILE.read_text(encoding="utf-8").strip()
    raise RuntimeError(
        f"No API key found. Set GEMMA_API_KEY env var or create {KEY_FILE}"
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
    """Tracks actual reported token usage in a rolling window and the time
    of the last request, and waits as needed before the next call."""

    def __init__(self):
        self.last_request_time = 0.0
        self.usage_log = []  # list of (timestamp, total_tokens)

    def wait_if_needed(self):
        now = time.time()

        since_last = now - self.last_request_time
        if since_last < MIN_SECONDS_BETWEEN_REQUESTS:
            time.sleep(MIN_SECONDS_BETWEEN_REQUESTS - since_last)

        now = time.time()
        self.usage_log = [
            (t, tok) for (t, tok) in self.usage_log if now - t < ROLLING_WINDOW_SECONDS
        ]
        window_total = sum(tok for _, tok in self.usage_log)
        if window_total >= TPM_SAFETY_CAP and self.usage_log:
            oldest_t = self.usage_log[0][0]
            sleep_for = ROLLING_WINDOW_SECONDS - (time.time() - oldest_t) + 0.5
            if sleep_for > 0:
                print(f"  (rate limit guard: sleeping {sleep_for:.1f}s -- "
                      f"{window_total} tokens used in trailing 60s)")
                time.sleep(sleep_for)

    def record(self, total_tokens):
        self.last_request_time = time.time()
        self.usage_log.append((self.last_request_time, total_tokens))


def generate(api_key, prompt, limiter, max_retries=3):
    limiter.wait_if_needed()

    body = {"contents": [{"parts": [{"text": prompt}]}]}
    url = f"{API_URL}?key={api_key}"

    for attempt in range(max_retries):
        resp = requests.post(url, json=body, timeout=120)
        if resp.status_code == 429:
            wait = 30 * (attempt + 1)
            print(f"  (429 rate limited -- waiting {wait}s, attempt {attempt+1}/{max_retries})")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        result = resp.json()
        usage = result.get("usageMetadata", {})
        limiter.record(usage.get("totalTokenCount", 0))
        return result

    raise RuntimeError("Exceeded max retries on 429 rate limiting")


def extract_texts(result):
    """Split the response into (thinking_text, final_text). Gemini marks
    reasoning parts with "thought": true -- distinct from Ollama's separate
    top-level "thinking" field, so this needs its own extraction, not reuse
    of the Ollama-side logic."""
    candidates = result.get("candidates", [])
    if not candidates:
        return "", ""
    parts = candidates[0].get("content", {}).get("parts", [])
    thinking_parts = [p.get("text", "") for p in parts if p.get("thought")]
    final_parts = [p.get("text", "") for p in parts if not p.get("thought")]
    return "\n\n".join(thinking_parts), "\n\n".join(final_parts)


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
                    thinking_text, final_text = extract_texts(result)
                    usage = result.get("usageMetadata", {})

                    record = {
                        "raw_api_response": result,
                        "thinking_text": thinking_text,
                        "final_text": final_text,
                        "prompt_token_count": usage.get("promptTokenCount"),
                        "candidates_token_count": usage.get("candidatesTokenCount"),
                        "thoughts_token_count": usage.get("thoughtsTokenCount"),
                        "total_token_count": usage.get("totalTokenCount"),
                        "_meta": {
                            "model": MODEL,
                            "provider": "google_ai_studio",
                            "task": task,
                            "condition": condition,
                            "sample_idx": sample_idx,
                            "prompt_text": prompt_text,
                            "elapsed_seconds": elapsed,
                            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        },
                    }
                    with open(fpath, "w", encoding="utf-8") as f:
                        json.dump(record, f, ensure_ascii=False, indent=2)
                    print(f"{label} -- ok ({elapsed:.1f}s, "
                          f"{usage.get('totalTokenCount')} tokens)")
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
