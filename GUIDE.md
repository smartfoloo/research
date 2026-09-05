# Guide — start here

CLAUDE.md is the full reference (rules, hypotheses, threats to validity). This
file is the simple version: what to actually do, in order, at the minimum bar
needed for the research to work. Improve things later, not now.

## The one-sentence project

Compare 4 ways of handling a Japanese coding prompt (raw / +directive /
machine-translated / English-original) and see which one gets closest to
English performance, and at what cost.

## Minimum viable plan

1. **10 coding tasks.** Simple algorithm problems. You must understand each one
   well enough to explain it out loud before writing a prompt for it.
2. **1 local model** that shows its reasoning steps.
3. **4 prompt versions per task**: JA-raw, JA+directive, MT-EN, EN-human.
4. **5 runs per version per task.** Record: pass/fail, token counts.
5. **Look at the numbers.** Does JA-raw do worse than EN-human? Does anything
   close the gap?

That's it. That's a complete first result.

## Steps, in order

- [x] `git init` in this folder — done, branch renamed to `main`
- [x] Pick the 10 tasks (drafted — see below; also built out as full specs,
      prompts, and test suites in `spike/`)
- [x] Write the English version of each task — see `spike/prompts-en.md`
- [ ] Write the Japanese version yourself, from the English spec (not a
      translation of your own English prompt — write it fresh in Japanese,
      calibrated against real Japanese coding-problem sources like AtCoder/
      Qiita first). Fill into `spike/prompts.json` under `ja_raw`.
- [ ] Add `ja_directive` and `mt_en` versions to `spike/prompts.json` once
      `ja_raw` is settled
- [ ] Get local models running, confirm GPU use and reasoning traces —
      see "PC setup" below
- [ ] Run 5 samples × 10 tasks × 4 conditions, save every raw output —
      `spike/run_generations.py` does this automatically
- [ ] Grade the outputs — `spike/grade_generations.py` does this automatically
- [ ] Look at it. Does a gap exist? Does anything close it?

If the last step shows nothing interesting, that's fine — see "if it doesn't
work" below.

## The 10 tasks (draft, locked for the spike)

**Simple:** reverse-words-preserving-punctuation, dedupe-and-sort-list,
business-days-between-dates, validate-email-format, format-number-as-currency

**Complex:** expression-evaluator-with-precedence, lru-cache-with-ttl,
shortest-path-with-route, bank-transactions-with-rollback,
meeting-room-scheduler

Don't touch these until after the spike runs once. Changing tasks before you
have a result is how projects stall.

## Do not do yet (later-you problems, not now-you problems)

These make the paper stronger. None of them are needed to get a first result.
Add them only after the basic loop above works.

- Second bilingual person to check your Japanese
- Back-translation of your Japanese prompts
- Multiple models / frontier API models
- More than 10 tasks
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
Note: any condition still `null` in `prompts.json` is skipped automatically.
Until the Japanese prompts are filled in, this only generates **EN-human** —
useful for testing the harness, not yet the real result.

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
