# Guide — start here

CLAUDE.md is the full reference (rules, hypotheses, threats to validity). This
file is the simple version: what to actually do, in order, at the minimum bar
needed for the research to work. Improve things later, not now.

## The one-sentence project

Compare 4 ways of handling a Japanese coding prompt (raw / +directive /
machine-translated / English-original) and see which one gets closest to
English performance, and at what cost.

## Status (2026-09-06): pipeline unblocked, ready to run

**2-day presentation deadline** — results shown don't need to be final or
fully accurate, just real and honestly labeled as preliminary. See CLAUDE.md
Status section for the full list of deliberate scope cuts made to hit this.

All prompt-authoring work is done. All that's left is: run generation → grade
→ look at the numbers → build the presentation.

## Minimum viable plan (as scoped for the deadline)

1. **6 coding tasks** (cut from 10 — see below). You understand each one well
   enough to explain it out loud; that's why they were picked.
2. **1 local model** (`qwen3.5:9b`) that shows its reasoning steps.
   `deepseek-r1:14b`/`gemma4:12b` are bonus-only, don't block on them.
3. **4 prompt versions per task**: JA-raw, JA+directive, MT-EN, EN-human — all
   written and filled into `spike/prompts.json` already.
4. **3 runs per version per task.** Record: pass/fail, token counts.
5. **Look at the numbers.** Does JA-raw do worse than EN-human? Does anything
   close the gap?

That's it. That's a complete first result.

## Steps, in order

- [x] `git init` — done, branch `main`, pushed to GitHub
- [x] Pick the 6 tasks (cut from original 10 — see below)
- [x] Write the English version of each task — `spike/prompts-en.md`
- [x] Write the Japanese version — `spike/prompts-ja.md`, filled into
      `spike/prompts.json` under `ja_raw`
- [x] `ja_directive` and `mt_en` filled into `spike/prompts.json` — all 6
      tasks now have all 4 conditions
- [ ] Get `qwen3.5:9b` running on the PC, confirm GPU use and reasoning
      traces — see "PC setup" below
- [ ] Run 3 samples × 6 tasks × 4 conditions, save every raw output —
      `spike/run_generations.py` does this automatically
- [ ] Grade the outputs — `spike/grade_generations.py` does this automatically
- [ ] Look at it. Does a gap exist? Does anything close it?
- [ ] Build the presentation — preliminary results, labeled as such (small N,
      one local model, spike not full study)

If the results step shows nothing interesting, that's fine — see "if it
doesn't work" below.

## The 6 tasks (cut from 10 for the deadline)

**Simple:** business-days, currency-format, reverse-list-elements

**Complex:** eval-expression, shortest-path, bank-rollback

Cut: dedupe-sort, valid-email (ceiling risk, low signal), lru-ttl-cache
(grading already scoped to LRU-only), meeting-rooms (redundant with
bank-rollback/shortest-path). Full 10 still in `spike/task-specs-en.md` for
the real study later.

Don't touch these until after the spike runs once. Changing tasks before you
have a result is how projects stall.

## Do not do yet (later-you problems, not now-you problems)

These make the paper stronger. None of them are needed for the presentation.
Add them only after the deadline, for the real study.

- Second bilingual person to check your Japanese
- Back-translation verification of your Japanese prompts
- Multiple models / frontier API models
- More than 6 tasks
- Formal statistics (right now: just look at the numbers)
- Preregistration
- Citing/reading every related paper in full
- Web app / iOS / server tasks (a different project — see CLAUDE.md)
- Deciding on a venue

## PC setup and running the pipeline

The research files live in this repo (edited via Mac/Claude Code). The actual
model generation runs on the separate PC with the RTX 4060 Ti — that machine
needs its own setup. Do these steps there.

### 1. Get the repo onto the PC

If pushing to a private GitHub repo (ask first if you'd rather transfer some
other way — network share, USB):
```bash
gh repo create research --private --source=. --remote=origin
git commit -m "Initial spike setup"
git push -u origin main
```
Then on the PC:
```bash
git clone <the-repo-url>
cd research
```

### 2. Ollama

```bash
ollama pull qwen3.5:9b
ollama pull deepseek-r1:14b
ollama pull gemma4:12b
```
Verify GPU use — run a model, then in another terminal:
```bash
ollama ps
```
Should show ~100% GPU, not split with CPU. Also watch `nvidia-smi` VRAM usage
during generation — some of these are "tight fits" on 8GB VRAM and may spill
under a long reasoning trace even if they load fine.

### 3. Docker

Install Docker Desktop (needs WSL2 backend on Windows). Verify:
```bash
docker run --rm python:3.11-slim python -c "print('ok')"
```

### 4. Python environment

```bash
cd research
python -m venv .venv
.venv\Scripts\activate     # Windows
pip install requests
```

### 5. Run it

```bash
cd spike
python run_generations.py
```
All 4 conditions are filled for all 6 tasks now — this generates the real
spike data: 6 tasks × 4 conditions × 3 samples = 72 generations on
`qwen3.5:9b`.

Then grade:
```bash
python grade_generations.py
```
Check results:
```bash
cat ../data/raw/*.grade.json | grep all_passed
```

## If it doesn't work

- **No gap between JA-raw and EN-human at all** → try a harder task or a
  bigger local model before concluding there's nothing here.
- **Gap exists but nothing closes it** → still a result. Write it up as "we
  tried, it didn't work" — that's honest and publishable.
- **You get confused mid-way** → stop, come back to this file, do the next
  unchecked box only. Don't redesign the whole thing again.

## Where things live

- `CLAUDE.md` — full rules and reasoning, read when you want the "why"
- `GUIDE.md` — this file, the "what do I do right now"
- `NOTEBOOK.md` — your dated log, write in it every session
- `lit/` — notes on papers you've read
- `data/raw/` — saved model outputs, never edited after saving
