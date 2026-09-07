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

## Read

- Real gap + ja_directive recovery only on qwen3.5 (weakest model, smallest/quantized). Gap: 67%→53% (mt_en worst). ja_directive: 94%, near-ceiling, at ~3-4x token cost. (Stale — pending regen, but the local arm's own prompts were never affected by the backtick fix since business-days aside its ja_raw already had backticks; direction of finding unlikely to change.)
- Ceiling effect on every other model tested so far (87-99% overall) — task set can't show a language effect on models this strong, now confirmed on 4 different capable models (Gemma, flash-lite, Groq's qwen3.8-27b, Luna). flash-lite is the one exception worth noting: `ja_directive` is its *worst* condition (78%), not its best — it has no reasoning trace to redirect, so the directive can't help and just adds cost (~2x tokens for a worse result).
- Luna's `ja_directive` costs only ~1.13x en_human — the smallest directive markup of any model tested, well below even Gemma's ~1.2x. Consistent with the pattern across every capable model so far: a strong model has little/no real gap to close, so it doesn't pay much to "close" it either.
- Reasoning-trace visibility: qwen3.5 (yes, bundled in output), gemma (yes, separate `thought` parts), and luna (partial — abbreviated reasoning *summary* text via the Responses API, not the full trace, but genuinely checkable/language-taggable). flash-lite and Groq's qwen3.8-27b return no reasoning trace at all — no mechanism check possible on those two.
- Luna cost: $0.095 total for all 144 generations (real, billed). Cheapest per-generation of any hosted-API arm by output token volume, despite being the only paid one.
