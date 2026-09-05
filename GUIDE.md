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

- [ ] `git init` in this folder
- [ ] Pick the 10 tasks (already drafted — see below)
- [ ] Write the English version of each task (plain description, no ambiguity)
- [ ] Write the Japanese version yourself, from the English spec (not a
      translation of your own English prompt — write it fresh in Japanese)
- [ ] Get one local model running, confirm you can see its reasoning + token
      counts
- [ ] Run 5 samples × 10 tasks × 4 conditions, save every raw output
- [ ] Put pass/fail + token counts in a spreadsheet
- [ ] Look at it. Does a gap exist? Does anything close it?

If step 8 shows nothing interesting, that's fine — see "if it doesn't work"
below.

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
