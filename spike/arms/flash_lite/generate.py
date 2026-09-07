"""
Self-contained generation runner for the gemini-3.5-flash-lite arm.

Same structure as the Gemma arm's generate.py, adjusted for a different
model on the same Google AI Studio key: different rate limits (15 RPM / 500
RPD, vs Gemma's 30 RPM / 16K TPM), and no thinking support at all (confirmed
empirically -- flash-lite returns no "thought" part and no thoughtsTokenCount
even with thinkingConfig.includeThoughts set, so we don't send that config
here). Separate output directory, separate file -- zero risk to the other
two arms.

Usage (from anywhere):
  python spike/arms/flash_lite/generate.py

Requires spike/.gemma_api_key (same key as the Gemma arm -- same Google AI
Studio account) or the GEMMA_API_KEY environment variable.
"""

import json
import time
import requests
from pathlib import Path

MODEL = "gemini-3.5-flash-lite"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

CONDITIONS = ["en_human", "ja_raw", "ja_directive", "mt_en"]
SAMPLES_PER_CELL = 6  # match the other two arms directly -- no pilot needed,
# this model shares infrastructure already validated on Gemma.

# Confirmed: 15 RPM, 500 RPD. TPM not confirmed for this specific model --
# reusing the same conservative rolling-window guard that worked cleanly for
# Gemma rather than assuming a higher number.
MIN_SECONDS_BETWEEN_REQUESTS = 4.5  # 60/15=4s minimum for 15 RPM; margin added
TPM_SAFETY_CAP = 12000
ROLLING_WINDOW_SECONDS = 60

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PROMPTS_FILE = ROOT / "spike" / "prompts.json"
OUT_DIR = ROOT / "data" / "raw" / "flash_lite"
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
    def __init__(self):
        self.last_request_time = 0.0
        self.usage_log = []

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
    """flash-lite doesn't return "thought": true parts at all (confirmed
    empirically), so thinking_text will always come back empty here -- this
    function is identical to the Gemma version and handles that correctly:
    a part with no "thought" key is falsy, so it's treated as final text."""
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
