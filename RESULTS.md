# Spike Results (2026-09-06/07)

4 conditions × 6 tasks × N=6 samples = 144 generations per model. See `CLAUDE.md` for full methodology/caveats.

**Note on data currency (2026-09-07):** `en_human`/`mt_en` backtick-formatting was fixed for 5 of 6 core tasks (see `CLAUDE.md` Status). **flash-lite** and **luna** below reflect the corrected prompts. **qwen3.5:9b, gemma-4-31b-it, and Groq's qwen3.8-27b are stale** — still from the pre-fix run, regeneration pending for those three.

## Pass rate by condition

| condition | qwen3.5:9b (local, stale) | gemma-4-31b-it (stale) | gemini-3.5-flash-lite | qwen/qwen3.8-27b (Groq, stale) | gpt-5.6-luna |
|---|---|---|---|---|---|
| en_human | 24/36 (67%) | 35/36 (97%) | 36/36 (100%) | 32/36 (89%) | 35/36 (97%) |
| ja_raw | 23/36 (64%) | 35/36 (97%) | 33/36 (92%) | 30/36 (83%) | 36/36 (100%) |
| **ja_directive** | **34/36 (94%)** | 36/36 (100%) | 28/36 (78%) | 32/36 (89%) | 35/36 (97%) |
| mt_en | 19/36 (53%) | 36/36 (100%) | 32/36 (89%) | 31/36 (86%) | 35/36 (97%) |
| **overall** | 100/144 (69%) | 142/144 (99%) | 129/144 (90%) | 125/144 (87%) | 141/144 (98%) |

## Avg tokens/generation (indexed to that model's own en_human)

| condition | qwen3.5:9b (stale) | gemma-4-31b-it (stale) | flash-lite | Groq qwen3.8-27b (stale) | luna |
|---|---|---|---|---|---|
| en_human | 1380 (1.00x) | 1531 (1.00x) | 628 (1.00x) | 502 (1.00x) | 612 (1.00x) |
| ja_raw | 1845 (1.34x) | 1644 (1.07x) | 756 (1.20x) | 514 (1.02x) | 673 (1.10x) |
| ja_directive | 5302 (3.84x) | 1889 (1.23x) | 1238 (1.97x) | 1146 (2.28x) | 694 (1.13x) |
| mt_en | 1609 (1.17x) | 1499 (0.98x) | 616 (0.98x) | 536 (1.07x) | 613 (1.00x) |

## Tokens per correct solution

| condition | qwen3.5:9b (stale) | gemma-4-31b-it (stale) | flash-lite | Groq qwen3.8-27b (stale) | luna |
|---|---|---|---|---|---|
| en_human | 2069 | 1575 | 628 | 564 | 630 |
| ja_raw | 2887 | 1691 | 825 | 617 | 673 |
| ja_directive | 5614 | 1889 | 1592 | 1290 | 714 |
| mt_en | 3048 | 1499 | 693 | 623 | 631 |

## Bonus/exploratory tasks (simulate-snake, apply-rewrite-rules) — 2026-09-08

**Not part of the main 6-task claim-bearing result** — see `CLAUDE.md` Status. Same N=6/cell, same 4 conditions, only flash-lite and luna run so far (the two models already at ceiling on the core 6). Test cases for these two tasks (`spike/test_cases.py`) were authored and hand-verified for this run; `grading_common.py`'s tuple/list normalization was made recursive at the same time (previously only the top-level return value was normalized, which happened not to matter for any of the core 6 but would have silently failed correct solutions here, where `simulate_snake` returns a list of coordinate tuples nested inside the result).

### Pass rate by condition (2 bonus tasks only)

| condition | gemini-3.5-flash-lite | gpt-5.6-luna |
|---|---|---|
| en_human | 12/12 (100%) | 12/12 (100%) |
| ja_raw | 12/12 (100%) | 12/12 (100%) |
| ja_directive | 10/12 (83%) | 12/12 (100%) |
| mt_en | 11/12 (92%) | 11/12 (92%) |
| **overall** | 45/48 (94%) | 47/48 (98%) |

By task: `apply-rewrite-rules` is at a full ceiling on both models (24/24, 100%, every condition) — it did not succeed at getting either model off the ceiling. `simulate-snake` shows some texture: flash-lite 21/24 (88%), luna 23/24 (96%).

### Avg tokens/generation (indexed to that model's own en_human, bonus tasks only)

| condition | flash-lite | luna |
|---|---|---|
| en_human | 1436 (1.00x) | 2172 (1.00x) |
| ja_raw | 1657 (1.15x) | 2480 (1.14x) |
| ja_directive | 1965 (1.37x) | 2491 (1.15x) |
| mt_en | 1486 (1.04x) | 2224 (1.02x) |

### Tokens per correct solution (bonus tasks only)

| condition | flash-lite | luna |
|---|---|---|
| en_human | 1436 | 2172 |
| ja_raw | 1657 | 2480 |
| ja_directive | 1966 | 2491 |
| mt_en | 1492 | 2201 |

### Read (bonus tasks)

- Still a ceiling effect on both models overall (94%, 98%) — these two tasks did not manage to push either model into a regime where a language effect could show, despite being harder than the core 6 by design.
- flash-lite's one real crack: `ja_directive` is again its worst condition (83%, same direction as the core-6 result), at ~1.37x the token cost of `en_human` for a worse pass rate — consistent with "no reasoning trace to redirect, so the directive only adds cost."
- The two flash-lite `simulate-snake` failures traced by hand: one got the tail-movement exception wrong (treated a same-turn tail vacancy as a fatal collision), one ignored the opposite-direction override and just applied the requested reversal literally, one had a growth/shrink tracking bug that left a stale extra segment after a non-growing move. All three are genuine model bugs on subtle spec details, not test-harness artifacts.
- luna's one failure (`simulate-snake`/`mt_en`/sample2) graded 0/6 because its first fenced code block contained a broken self-correction (an incomplete `walrus`-operator line, no trailing `return`) that it then fixed in a second code block later in the same response — `grading_common.py` only ever grades the first fenced block by design (documented, applies identically to every arm), so this is the existing methodology working as intended, not a luna-specific bug.
- `apply-rewrite-rules` turned out to be an easier ceiling-breaker candidate than `simulate-snake` was hoped to be — both models solved it perfectly in all 24 samples each. If a future harder bonus task is authored, this is a data point that URL/rule-matching logic (however many branches) is not where these two models struggle; state-machine simulation with several interacting edge cases (like `simulate-snake`) is closer to where cracks show.

## Combined 8-task overall (core 6 + 2 bonus) — flash-lite and luna only

The two models with a complete 8-task × 4-condition × N=6 dataset (192 samples each — the only two run on both bonus tasks so far). Not a new dataset, just the core-6 and bonus-2 numbers above summed together per model.

| condition | gemini-3.5-flash-lite | gpt-5.6-luna |
|---|---|---|
| en_human | 48/48 (100%) | 47/48 (98%) |
| ja_raw | 45/48 (94%) | 48/48 (100%) |
| ja_directive | 38/48 (79%) | 47/48 (98%) |
| mt_en | 43/48 (90%) | 46/48 (96%) |
| **overall** | 174/192 (91%) | 188/192 (98%) |

| tokens | flash-lite avg (indexed) | flash-lite tok/correct | luna avg (indexed) | luna tok/correct |
|---|---|---|---|---|
| en_human | 830 (1.00x) | 830 | 1002 (1.00x) | 1023 |
| ja_raw | 982 (1.18x) | 1047 | 1125 (1.12x) | 1125 |
| ja_directive | 1420 (1.71x) | 1793 | 1143 (1.14x) | 1168 |
| mt_en | 833 (1.00x) | 930 | 1016 (1.01x) | 1060 |

Adding the 2 harder bonus tasks pulled flash-lite's overall down from 90% (core 6 alone) to 91% combined — basically unchanged, and its `ja_directive` gap actually widened slightly (78%→79% core vs the combined number sitting closer to the bonus tasks' 83%, both still clearly its worst condition). Luna barely moved (98%→98%). Neither model came off its ceiling in a way that changes the story: both are still too strong for this task set, bonus tasks included.

## Read

- Real gap + ja_directive recovery only on qwen3.5 (weakest model, smallest/quantized). Gap: 67%→53% (mt_en worst). ja_directive: 94%, near-ceiling, at ~3-4x token cost. (Stale — pending regen, but the local arm's own prompts were never affected by the backtick fix since business-days aside its ja_raw already had backticks; direction of finding unlikely to change.)
- Ceiling effect on every other model tested so far (87-99% overall) — task set can't show a language effect on models this strong, now confirmed on 4 different capable models (Gemma, flash-lite, Groq's qwen3.8-27b, Luna). flash-lite is the one exception worth noting: `ja_directive` is its *worst* condition (78%), not its best — it has no reasoning trace to redirect, so the directive can't help and just adds cost (~2x tokens for a worse result).
- Luna's `ja_directive` costs only ~1.13x en_human — the smallest directive markup of any model tested, well below even Gemma's ~1.2x. Consistent with the pattern across every capable model so far: a strong model has little/no real gap to close, so it doesn't pay much to "close" it either.
- Reasoning-trace visibility: qwen3.5 (yes, bundled in output), gemma (yes, separate `thought` parts), and luna (partial — abbreviated reasoning *summary* text via the Responses API, not the full trace, but genuinely checkable/language-taggable). flash-lite and Groq's qwen3.8-27b return no reasoning trace at all — no mechanism check possible on those two.
- Luna cost: $0.095 total for all 144 generations (real, billed). Cheapest per-generation of any hosted-API arm by output token volume, despite being the only paid one.
