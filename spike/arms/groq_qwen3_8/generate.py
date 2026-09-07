"""
Self-contained generation runner for the Groq / qwen-3.8-27b arm.

Separate provider, separate API shape (OpenAI-compatible chat completions,
not Gemini's contents/parts schema), separate output directory. Zero overlap
with the local, Gemma, or flash-lite arms.

Confirmed empirically before writing this: qwen/qwen3.8-27b on Groq returns
no reasoning/thinking content at all (plain message.content only, even on a
real shortest-path-style prompt) -- same as flash-lite. This arm gives
pass/fail + token counts only, no mechanism-check data.

Also confirmed: Groq echoes the actual per-request seed used
(x_groq.seed) -- captured in _meta for free, better reproducibility logging
than either the local or Gemini arms have.

Usage (from anywhere):
  python spike/arms/groq_qwen3_8/generate.py

Requires spike/.groq_api_key (gitignored) or the GROQ_API_KEY env var.

Rate limits (Free tier, confirmed against Groq's own docs, 2026-09-06):
  30 RPM, 1,000 RPD, 8,000 TPM, 200,000 TPD (qwen/qwen3.8-27b specifically).
TPD is the real constraint over a full 144-call run (RPD has huge margin) --
this script tracks a running daily total and stops before exceeding it,
rather than finding out via a 429 partway through.
"""

import json
import time
import requests
from pathlib import Path

MODEL = "qwen/qwen3.8-27b"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

CONDITIONS = ["en_human", "ja_raw", "ja_directive", "mt_en"]
SAMPLES_PER_CELL = 6  # match the other three arms

MIN_SECONDS_BETWEEN_REQUESTS = 12  # documented limit is 30 RPM (2s min), but
# in practice nearly every request at 2.5s spacing hit a 429 -- the real
# enforced limit is clearly stricter than what's published. One-at-a-time,
# with real spacing, rather than leaning on retry-after-429 backoff.
TPM_SAFETY_CAP = 6500  # under the confirmed 8,000 TPM
ROLLING_WINDOW_SECONDS = 60
TPD_SAFETY_CAP = 180000  # under the confirmed 200,000 TPD, real margin left
# for retries/reruns without needing to track resets across a day boundary

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PROMPTS_FILE = ROOT / "spike" / "prompts.json"
OUT_DIR = ROOT / "data" / "raw" / "groq_qwen3_8"
KEY_FILE = ROOT / "spike" / ".groq_api_key"


def load_api_key():
    import os
    env_key = os.environ.get("GROQ_API_KEY")
    if env_key:
        return env_key.strip()
    if KEY_FILE.exists():
        return KEY_FILE.read_text(encoding="utf-8").strip()
    raise RuntimeError(
        f"No API key found. Set GROQ_API_KEY env var or create {KEY_FILE}"
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


def count_tokens_already_used_today():
    """Sum total_tokens across every raw file already saved by THIS script
    today, so a resumed/re-run session knows how much of the daily 200K TPD
    it's already spent, rather than assuming a fresh budget on every run."""
    today = time.strftime("%Y-%m-%d")
    used = 0
    for f in OUT_DIR.glob("*.json"):
        if f.name.endswith(".grade.json"):
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        gen_at = d.get("_meta", {}).get("generated_at", "")
        if gen_at.startswith(today):
            used += d.get("total_tokens") or 0
    return used


class RateLimiter:
    def __init__(self, tpd_already_used):
        self.last_request_time = 0.0
        self.usage_log = []  # rolling 60s window, for TPM
        self.tpd_used = tpd_already_used

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
                print(f"  (TPM guard: sleeping {sleep_for:.1f}s -- "
                      f"{window_total} tokens used in trailing 60s)")
                time.sleep(sleep_for)

    def record(self, total_tokens):
        self.last_request_time = time.time()
        self.usage_log.append((self.last_request_time, total_tokens))
        self.tpd_used += total_tokens

    def tpd_budget_left(self):
        return TPD_SAFETY_CAP - self.tpd_used


def generate(api_key, prompt, limiter, max_retries=3):
    limiter.wait_if_needed()

    body = {"model": MODEL, "messages": [{"role": "user", "content": prompt}]}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    for attempt in range(max_retries):
        resp = requests.post(API_URL, json=body, headers=headers, timeout=120)
        if resp.status_code == 429:
            wait = 30 * (attempt + 1)
            print(f"  (429 rate limited -- waiting {wait}s, attempt {attempt+1}/{max_retries})")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        result = resp.json()
        usage = result.get("usage", {})
        limiter.record(usage.get("total_tokens", 0))
        return result

    raise RuntimeError("Exceeded max retries on 429 rate limiting")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    prompts = load_prompts()
    tpd_used = count_tokens_already_used_today()
    limiter = RateLimiter(tpd_used)
    print(f"TPD already used today (from existing files): {tpd_used}")

    total = len(prompts) * len(CONDITIONS) * SAMPLES_PER_CELL
    done = 0
    skipped_existing = 0
    failed = []
    stopped_for_tpd = False

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

                if limiter.tpd_budget_left() <= 0:
                    print(f"{label} -- STOPPING: TPD safety cap ({TPD_SAFETY_CAP}) reached. "
                          f"Resume tomorrow, or after the daily quota resets.")
                    stopped_for_tpd = True
                    break

                try:
                    t0 = time.time()
                    result = generate(api_key, prompt_text, limiter)
                    elapsed = time.time() - t0
                    msg = result["choices"][0]["message"]
                    usage = result.get("usage", {})

                    record = {
                        "raw_api_response": result,
                        "response_text": msg.get("content", ""),
                        "finish_reason": result["choices"][0].get("finish_reason"),
                        "prompt_tokens": usage.get("prompt_tokens"),
                        "completion_tokens": usage.get("completion_tokens"),
                        "total_tokens": usage.get("total_tokens"),
                        "groq_seed": result.get("x_groq", {}).get("seed"),
                        "_meta": {
                            "model": MODEL,
                            "provider": "groq",
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
                          f"{usage.get('total_tokens')} tokens, "
                          f"tpd_left={limiter.tpd_budget_left()})")
                except Exception as e:
                    failed.append(label)
                    print(f"{label} -- FAILED: {e}")
            if stopped_for_tpd:
                break
        if stopped_for_tpd:
            break

    print("\n--- run complete ---" if not stopped_for_tpd else "\n--- run stopped early (TPD cap) ---")
    print(f"total slots:            {total}")
    print(f"skipped (already done): {skipped_existing}")
    print(f"failed:                 {len(failed)}")
    if failed:
        print("failed runs:")
        for f in failed:
            print(f"  {f}")


if __name__ == "__main__":
    main()
