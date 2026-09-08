# Spike Results (2026-09-06/07)

4 conditions × 6 tasks × N=6 samples = 144 generations per model. See `CLAUDE.md` for full methodology/caveats.

**Note on data currency (2026-09-08):** `en_human`/`mt_en` backtick-formatting was fixed for 5 of 6 core tasks (see `CLAUDE.md` Status). **qwen3.5:9b, flash-lite, and luna** below reflect the corrected prompts. **gemma-4-31b-it and Groq's qwen3.8-27b are still stale** — from the pre-fix run, regeneration pending for those two.

## Pass rate by condition

| condition | qwen3.5:9b (local) | gemma-4-31b-it (stale) | gemini-3.5-flash-lite | qwen/qwen3.8-27b (Groq, stale) | gpt-5.6-luna |
|---|---|---|---|---|---|
| en_human | 24/36 (67%) | 35/36 (97%) | 36/36 (100%) | 32/36 (89%) | 35/36 (97%) |
| ja_raw | 23/36 (64%) | 35/36 (97%) | 33/36 (92%) | 30/36 (83%) | 36/36 (100%) |
| **ja_directive** | **34/36 (94%)** | 36/36 (100%) | 28/36 (78%) | 32/36 (89%) | 35/36 (97%) |
| mt_en | 25/36 (69%) | 36/36 (100%) | 32/36 (89%) | 31/36 (86%) | 35/36 (97%) |
| **overall** | 106/144 (74%) | 142/144 (99%) | 129/144 (90%) | 125/144 (87%) | 141/144 (98%) |

`mt_en` moved from worst condition (53%, pre-fix) to no longer the worst (69%) once it got genuine backtick-preserved Google Translate output instead of the stripped/paraphrased version — a real methodology fix changing a real number, not just cosmetic. `ja_raw`/`ja_directive` are unchanged (those two were never affected by the backtick bug for the core 6).

## Avg tokens/generation (indexed to that model's own en_human)

| condition | qwen3.5:9b | gemma-4-31b-it (stale) | flash-lite | Groq qwen3.8-27b (stale) | luna |
|---|---|---|---|---|---|
| en_human | 1346 (1.00x) | 1531 (1.00x) | 628 (1.00x) | 502 (1.00x) | 612 (1.00x) |
| ja_raw | 1845 (1.37x) | 1644 (1.07x) | 756 (1.20x) | 514 (1.02x) | 673 (1.10x) |
| ja_directive | 5302 (3.94x) | 1889 (1.23x) | 1238 (1.97x) | 1146 (2.28x) | 694 (1.13x) |
| mt_en | 1578 (1.17x) | 1499 (0.98x) | 616 (0.98x) | 536 (1.07x) | 613 (1.00x) |

## Tokens per correct solution

| condition | qwen3.5:9b | gemma-4-31b-it (stale) | flash-lite | Groq qwen3.8-27b (stale) | luna |
|---|---|---|---|---|---|
| en_human | 2019 | 1575 | 628 | 564 | 630 |
| ja_raw | 2887 | 1691 | 825 | 617 | 673 |
| ja_directive | 5614 | 1889 | 1592 | 1290 | 714 |
| mt_en | 2272 | 1499 | 693 | 623 | 631 |

## Bonus/exploratory tasks (simulate-snake, apply-rewrite-rules) — 2026-09-08

**Not part of the main 6-task claim-bearing result** — see `CLAUDE.md` Status. Same 4 conditions for all three models; N=6/cell for flash-lite and luna, **N=5 for qwen3.5 on `simulate-snake`/`ja_directive`** (see note below — one cell short a sample, not a data-quality issue). Test cases for these two tasks (`spike/test_cases.py`) were authored and hand-verified for this run; `grading_common.py`'s tuple/list normalization was made recursive at the same time (previously only the top-level return value was normalized, which happened not to matter for any of the core 6 but would have silently failed correct solutions here, where `simulate_snake` returns a list of coordinate tuples nested inside the result).

**qwen3.5 generation note:** one specific cell — `simulate-snake` × `ja_directive` × sample6 — failed 3 times in a row with an HTTP read timeout (600s, then twice at 1200s), a reproducible pattern distinct from this arm's normal pace, not a one-off. Read as a genuine degenerate/repetitive generation on this model for this specific prompt, not an infrastructure problem. Accepted as N=5 for that one cell rather than continuing to chase it.

### Pass rate by condition (2 bonus tasks only)

| condition | qwen3.5:9b (local) | gemini-3.5-flash-lite | gpt-5.6-luna |
|---|---|---|---|
| en_human | 1/12 (8%) | 12/12 (100%) | 12/12 (100%) |
| ja_raw | 3/12 (25%) | 12/12 (100%) | 12/12 (100%) |
| ja_directive | 2/11 (18%) | 10/12 (83%) | 12/12 (100%) |
| mt_en | 0/12 (0%) | 11/12 (92%) | 11/12 (92%) |
| **overall** | 6/47 (13%) | 45/48 (94%) | 47/48 (98%) |

By task: `apply-rewrite-rules` is at a full ceiling on flash-lite and luna (24/24, 100%, every condition) — did not succeed at getting either off the ceiling. `simulate-snake` shows some texture for those two: flash-lite 21/24 (88%), luna 23/24 (96%). **qwen3.5 collapses to near-floor on both tasks** — `apply-rewrite-rules` 4/24 (17%), `simulate-snake` 2/23 (9%) — the opposite failure mode from the other two arms' ceiling effect, and unlike them it's not just one task, both are equally out of reach. This is the first genuine floor effect seen anywhere in the spike (see CLAUDE.md's floor/ceiling-effects section) — these two tasks are hard enough that the weakest model can barely solve them at all, in any condition, so there's no room for a language effect to show here either, just from the other direction.

### Avg tokens/generation (indexed to that model's own en_human, bonus tasks only)

| condition | qwen3.5:9b | flash-lite | luna |
|---|---|---|---|
| en_human | 4894 (1.00x) | 1436 (1.00x) | 2172 (1.00x) |
| ja_raw | 10697 (2.19x) | 1657 (1.15x) | 2480 (1.14x) |
| ja_directive | 12848 (2.63x) | 1965 (1.37x) | 2491 (1.15x) |
| mt_en | 4189 (0.86x) | 1486 (1.04x) | 2224 (1.02x) |

qwen3.5's token cost on these two tasks is enormous relative to the core 6 (4-9x the core-6 average depending on condition) and `ja_directive` pushes it further still (2.63x its own `en_human`, similar shape to the core-6 3.94x blowup) — consistent with a weak model burning huge amounts of test-time compute on tasks it still mostly can't solve.

### Tokens per correct solution (bonus tasks only)

| condition | qwen3.5:9b | flash-lite | luna |
|---|---|---|---|
| en_human | 58731 | 1436 | 2172 |
| ja_raw | 42788 | 1657 | 2480 |
| ja_directive | 70663 | 1966 | 2491 |
| mt_en | N/A (0 correct) | 1492 | 2201 |

qwen3.5's cost-per-correct-solution on these two tasks is roughly 25-100x flash-lite's or luna's — the clearest H4 (cost ordering) result in the whole spike so far, though it's really a floor-effect artifact (almost nothing is correct, so the denominator is tiny) more than a meaningful cost comparison.

### Read (bonus tasks)

- flash-lite and luna: still a ceiling effect (94%, 98%) — these two tasks did not manage to push either model into a regime where a language effect could show, despite being harder than the core 6 by design.
- qwen3.5: the opposite problem — a floor effect. 13% overall, and `mt_en` is a clean 0/12. Too weak to solve these tasks in any condition, so no language effect is visible here either, just from underneath rather than above. `ja_raw` (25%) is qwen3.5's *best* condition on these two tasks, `ja_directive` second (18%, but off N=11) — genuinely different ordering from the core 6 result (where `ja_directive` was the clear best condition, 94%), worth noting as a real interaction rather than dismissing as noise, though N is thin enough here (11-12/cell, mostly single-digit successes) that it shouldn't be over-read.
- flash-lite's one real crack: `ja_directive` is again its worst condition (83%, same direction as the core-6 result), at ~1.37x the token cost of `en_human` for a worse pass rate — consistent with "no reasoning trace to redirect, so the directive only adds cost."
- The two flash-lite `simulate-snake` failures traced by hand: one got the tail-movement exception wrong (treated a same-turn tail vacancy as a fatal collision), one ignored the opposite-direction override and just applied the requested reversal literally, one had a growth/shrink tracking bug that left a stale extra segment after a non-growing move. All three are genuine model bugs on subtle spec details, not test-harness artifacts.
- luna's one failure (`simulate-snake`/`mt_en`/sample2) graded 0/6 because its first fenced code block contained a broken self-correction (an incomplete `walrus`-operator line, no trailing `return`) that it then fixed in a second code block later in the same response — `grading_common.py` only ever grades the first fenced block by design (documented, applies identically to every arm), so this is the existing methodology working as intended, not a luna-specific bug.
- `apply-rewrite-rules` turned out to be an easier ceiling-breaker candidate than `simulate-snake` was hoped to be for the two strong models — both solved it perfectly in all 24 samples each. Doesn't hold for qwen3.5 at all: both tasks are near-floor for it (17% and 9%), so "which task is harder for a capable model" and "which task is harder for a weak model" are answered by completely different data here — expected, but worth stating rather than assuming the two strong models' finding generalizes down.

## Combined 8-task overall (core 6 + 2 bonus)

All three models with a complete (or near-complete) 8-task × 4-condition dataset — qwen3.5 at N=6 except the one N=5 cell noted above (191/192 samples), flash-lite and luna at full N=6 (192/192 each). Not a new dataset, just the core-6 and bonus-2 numbers above summed together per model.

| condition | qwen3.5:9b (local) | gemini-3.5-flash-lite | gpt-5.6-luna |
|---|---|---|---|
| en_human | 25/48 (52%) | 48/48 (100%) | 47/48 (98%) |
| ja_raw | 26/48 (54%) | 45/48 (94%) | 48/48 (100%) |
| ja_directive | 36/47 (77%) | 38/48 (79%) | 47/48 (98%) |
| mt_en | 25/48 (52%) | 43/48 (90%) | 46/48 (96%) |
| **overall** | 112/191 (59%) | 174/192 (91%) | 188/192 (98%) |

| tokens | qwen3.5 avg (indexed) | qwen3.5 tok/correct | flash-lite avg (indexed) | flash-lite tok/correct | luna avg (indexed) | luna tok/correct |
|---|---|---|---|---|---|---|
| en_human | 2233 (1.00x) | 4288 | 830 (1.00x) | 830 | 1002 (1.00x) | 1023 |
| ja_raw | 4058 (1.82x) | 7491 | 982 (1.18x) | 1047 | 1125 (1.12x) | 1125 |
| ja_directive | 7068 (3.17x) | 9228 | 1420 (1.71x) | 1793 | 1143 (1.14x) | 1168 |
| mt_en | 2230 (1.00x) | 4283 | 833 (1.00x) | 930 | 1016 (1.01x) | 1060 |

Adding the 2 harder bonus tasks pulled flash-lite's overall down from 90% (core 6 alone) to 91% combined — basically unchanged, and its `ja_directive` gap actually widened slightly (78%→79% core vs the combined number sitting closer to the bonus tasks' 83%, both still clearly its worst condition). Luna barely moved (98%→98%). Neither strong model came off its ceiling in a way that changes the story. qwen3.5 moved a lot (74%→59% combined) because the bonus tasks are a genuine floor effect for it — but `ja_directive` stays its clearly-best condition at every level of aggregation (core 6 alone: 94%; combined: 77%), the one consistent finding across this whole spike regardless of which task subset you look at.

## Read

- Real gap + ja_directive recovery on qwen3.5 (weakest model, smallest/quantized), and now on current (non-stale) prompts: en_human 67%, ja_raw 64%, **ja_directive 94%**, mt_en 69% (mt_en used to be the clear worst pre-fix at 53% — now roughly tied with en_human/ja_raw, only ja_directive stands out). ja_directive is still the one condition that consistently helps this model, at ~4x token cost.
- Ceiling effect on every other model tested on the core 6 (87-99% overall) — task set can't show a language effect on models this strong, confirmed on 4 different capable models (Gemma, flash-lite, Groq's qwen3.8-27b, Luna). flash-lite is the one exception worth noting: `ja_directive` is its *worst* condition (78%), not its best — it has no reasoning trace to redirect, so the directive can't help and just adds cost (~2x tokens for a worse result).
- Luna's `ja_directive` costs only ~1.13x en_human — the smallest directive markup of any strong model tested, well below even Gemma's ~1.2x. Consistent with the pattern across every capable model so far: a strong model has little/no real gap to close, so it doesn't pay much to "close" it either.
- The 2 bonus tasks flip this entirely for qwen3.5: a genuine floor effect (13% overall, `mt_en` a clean 0/12) rather than the core 6's mixed-but-workable picture — see the bonus-tasks section above. `ja_directive` is still its best condition even at the floor (18%, vs `ja_raw`'s 25% — actually `ja_raw` edges it out here, the one place in the whole spike where `ja_directive` isn't clearly on top for this model, though N is thin enough not to lean hard on this).
- Reasoning-trace visibility: qwen3.5 (yes, bundled in output), gemma (yes, separate `thought` parts), and luna (partial — abbreviated reasoning *summary* text via the Responses API, not the full trace, but genuinely checkable/language-taggable). flash-lite and Groq's qwen3.8-27b return no reasoning trace at all — no mechanism check possible on those two.
- Luna cost: $0.095 total for all 144 core-6 generations (real, billed). Cheapest per-generation of any hosted-API arm by output token volume, despite being the only paid one.
- qwen3.5 local generation surfaced a genuine reliability issue worth flagging for the real study: one cell (`simulate-snake`/`ja_directive`/sample6) reproducibly failed 3 times with an HTTP read timeout, even at 1200s — a real degenerate-generation risk on this model/quantization that a fixed, generous timeout alone doesn't fully solve. Real study should budget for this (accept occasional N-1 cells, or add a hard retry-with-fresh-seed policy) rather than assume every cell completes.
