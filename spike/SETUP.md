# PC setup checklist — do this before running the spike

Do these in order. Test each step works before moving to the next — don't
build the whole pipeline blind and debug it all at once at the end.

## 1. Ollama

- Install from ollama.com if not already installed.
- Pull your models:
  ```bash
  ollama pull qwen3.5:9b
  ollama pull deepseek-r1:14b
  ollama list
  ```
  (llama3.1:8b already installed per your check.)

- Confirm GPU is actually being used, not silently falling back to CPU:
  ```bash
  ollama run qwen3.5:9b "say hi"
  ```
  while it's running, in another terminal:
  ```bash
  ollama ps
  ```
  Look for it showing 100% GPU (or close). If it shows a CPU/GPU split,
  that model is spilling into system RAM — expected for deepseek-r1:14b,
  should NOT happen for qwen3.5:9b or llama3.1:8b on your 8GB card.

- Also sanity-check with `nvidia-smi` while a model is generating — VRAM
  usage should jump up, confirming the GPU is actually loaded.

## 2. Docker (for isolated code execution/grading)

- Install Docker Desktop.
- On Windows: it needs WSL2 as the backend — the installer will prompt you
  to enable it if it's not already on.
- Verify it works:
  ```bash
  docker run --rm python:3.11-slim python -c "print('ok')"
  ```
  Should print `ok`. This is the same kind of container you'll run
  generated code in later.

## 3. Python environment for the scripting layer

You need a script that: sends a prompt to Ollama → gets the response →
extracts the code → runs it in a Docker container against your test cases →
records pass/fail + token counts.

- Set up a virtual environment in the repo:
  ```bash
  cd /Users/rios/research
  python -m venv .venv
  source .venv/bin/activate   # or .venv\Scripts\activate on Windows
  pip install requests
  ```
  (`requests` is enough to talk to Ollama's local API at
  `http://localhost:11434`. Add `docker` python package later if you want
  to drive containers from Python instead of shelling out.)

## 4. Repo basics

- `git init` if not already done (still outstanding per CLAUDE.md).
- Confirm the folder structure from GUIDE.md exists:
  ```
  research/
    CLAUDE.md
    GUIDE.md
    NOTEBOOK.md
    spike/
      task-specs-en.md
      prompts-en.md
      SETUP.md   (this file)
    data/raw/
    lit/
  ```

## 5. End-to-end test on ONE task before scaling up

Before running all 10 tasks × 4 conditions × 5 samples, prove the full
pipeline works on a single case:

1. Send task 2 (dedupe-sort) prompt to `qwen3.5:9b` via the API.
2. Save the raw response verbatim to `data/raw/`.
3. Extract just the Python function from the response.
4. Run it in a Docker container against the example (`[3,1,2,3,1]` →
   `[1,2,3]`).
5. Confirm you get a clean pass/fail result and can read token counts from
   Ollama's API response.

If this one case works cleanly, the same loop scales to all 10 tasks × 4
conditions × 5 samples — that's just more iterations of the same function,
not new engineering. If it doesn't work cleanly, you've found the problem
on 1 case instead of debugging it across 200.

## Notes

- Ollama's `/api/generate` endpoint returns token counts
  (`prompt_eval_count`, `eval_count`) directly in the response JSON — no
  separate tokenizer call needed for the local arm.
- Keep every raw response saved before you do any parsing/extraction on it —
  per CLAUDE.md, raw outputs are archived verbatim, never edited in place.
