"""
Unattended generation runner for the local qwen3.5:9b / Ollama arm.

Loops over model x task x condition x sample, calls the local Ollama API,
and saves every raw response verbatim to data/raw/qwen3_5_local/. Skips:
  - conditions with no prompt text yet (still null in prompts.json)
  - (model, task, condition, sample) combos already saved (resumable —
    safe to stop and re-run; it won't redo finished work)

Usage (from anywhere):
  python spike/arms/qwen3_5_local/generate.py

Requires Ollama running locally (default http://localhost:11434) with the
models below already pulled.
"""

import json
import time
import requests
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"

MODELS = [
    "qwen3.5:9b",
    # "deepseek-r1:14b",  # bonus-only if time remains — slower, tight VRAM fit
    # "gemma4:12b",       # bonus-only if time remains — slower, tight VRAM fit
]

CONDITIONS = ["en_human", "ja_raw", "ja_directive", "mt_en"]
SAMPLES_PER_CELL = 6  # bumped from 3: initial N=3 result was fragile/counter to
# H1, doubling to check whether it holds or was sampling noise. Still a spike,
# not the preregistered real study — say so in the presentation.

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PROMPTS_FILE = ROOT / "spike" / "prompts.json"
OUT_DIR = ROOT / "data" / "raw" / "qwen3_5_local"


def load_prompts():
    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.pop("_readme", None)
    return data


def out_path(model, task, condition, sample_idx):
    safe_model = model.replace(":", "-").replace("/", "-")
    fname = f"{safe_model}__{task}__{condition}__sample{sample_idx}.json"
    return OUT_DIR / fname


def generate(model, prompt):
    resp = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            # Ollama defaults to a 4096-token context if unset. ja_directive's
            # induced English reasoning traces alone were observed running
            # ~4000 tokens, leaving no room for the answer and truncating
            # (done_reason: "length") before any code was written. 8192
            # fixed all but one outlier sample, which needed more still;
            # 16384 is a no-op for every sample that never approached the
            # ceiling (num_ctx doesn't change sampling below it), so raising
            # it doesn't affect the 71 samples already generated under 8192.
            "options": {"num_ctx": 32768},
        },
        timeout=600,
    )
    resp.raise_for_status()
    return resp.json()


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    prompts = load_prompts()

    total = len(MODELS) * len(prompts) * len(CONDITIONS) * SAMPLES_PER_CELL
    done = 0
    skipped_missing = 0
    skipped_existing = 0
    failed = []

    for model in MODELS:
        for task, task_prompts in prompts.items():
            for condition in CONDITIONS:
                prompt_text = task_prompts.get(condition)
                for sample_idx in range(1, SAMPLES_PER_CELL + 1):
                    done += 1
                    label = f"[{done}/{total}] {model} | {task} | {condition} | sample{sample_idx}"

                    if prompt_text is None:
                        skipped_missing += 1
                        print(f"{label} -- skip (no prompt yet)")
                        continue

                    fpath = out_path(model, task, condition, sample_idx)
                    if fpath.exists():
                        skipped_existing += 1
                        print(f"{label} -- skip (already done)")
                        continue

                    try:
                        t0 = time.time()
                        result = generate(model, prompt_text)
                        elapsed = time.time() - t0
                        result["_meta"] = {
                            "model": model,
                            "task": task,
                            "condition": condition,
                            "sample_idx": sample_idx,
                            "prompt_text": prompt_text,
                            "elapsed_seconds": elapsed,
                            "generated_at": time.strftime(
                                "%Y-%m-%dT%H:%M:%S"
                            ),
                        }
                        with open(fpath, "w", encoding="utf-8") as f:
                            json.dump(result, f, ensure_ascii=False, indent=2)
                        print(f"{label} -- ok ({elapsed:.1f}s)")
                    except Exception as e:
                        failed.append(label)
                        print(f"{label} -- FAILED: {e}")

    print("\n--- run complete ---")
    print(f"total slots:      {total}")
    print(f"skipped (no prompt yet): {skipped_missing}")
    print(f"skipped (already done):  {skipped_existing}")
    print(f"failed:                  {len(failed)}")
    if failed:
        print("failed runs:")
        for f in failed:
            print(f"  {f}")


if __name__ == "__main__":
    main()
