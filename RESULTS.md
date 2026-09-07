# Spike Results (2026-09-06/07)

4 conditions × 6 tasks × N=6 samples = 144 generations per model. See `CLAUDE.md` for full methodology/caveats.

## Pass rate by condition

| condition | qwen3.5:9b (local) | gemma-4-31b-it | gemini-3.5-flash-lite | qwen/qwen3.8-27b (Groq) |
|---|---|---|---|---|
| en_human | 24/36 (67%) | 35/36 (97%) | 35/36 (97%) | 32/36 (89%) |
| ja_raw | 23/36 (64%) | 35/36 (97%) | 33/36 (92%) | 30/36 (83%) |
| **ja_directive** | **34/36 (94%)** | 36/36 (100%) | 28/36 (78%) | 32/36 (89%) |
| mt_en | 19/36 (53%) | 36/36 (100%) | 36/36 (100%) | 31/36 (86%) |
| **overall** | 100/144 (69%) | 142/144 (99%) | 132/144 (92%) | 125/144 (87%) |

## Avg tokens/generation (indexed to that model's own en_human)

| condition | qwen3.5:9b | gemma-4-31b-it | flash-lite | Groq qwen3.8-27b |
|---|---|---|---|---|
| en_human | 1380 (1.00x) | 1531 (1.00x) | 642 (1.00x) | 502 (1.00x) |
| ja_raw | 1845 (1.34x) | 1644 (1.07x) | 756 (1.18x) | 514 (1.02x) |
| ja_directive | 5302 (3.84x) | 1889 (1.23x) | 1238 (1.93x) | 1146 (2.28x) |
| mt_en | 1609 (1.17x) | 1499 (0.98x) | 621 (0.97x) | 536 (1.07x) |

## Tokens per correct solution

| condition | qwen3.5:9b | gemma-4-31b-it | flash-lite | Groq qwen3.8-27b |
|---|---|---|---|---|
| en_human | 2069 | 1575 | 660 | 564 |
| ja_raw | 2887 | 1691 | 825 | 617 |
| ja_directive | 5614 | 1889 | 1592 | 1290 |
| mt_en | 3048 | 1499 | 621 | 623 |

## Read

- Real gap + ja_directive recovery only on qwen3.5 (weakest model, smallest/quantized). Gap: 67%→53% (mt_en worst). ja_directive: 94%, near-ceiling, at ~3-4x token cost.
- Ceiling effect on the other three models (92-99% overall) — task set can't show a language effect on models this strong. flash-lite is the one exception worth noting: ja_directive is its *worst* condition (78%), not its best — it has no reasoning trace to redirect, so the directive can't help and just adds cost.
- Reasoning-trace visibility: qwen3.5 (yes, bundled in output) and gemma (yes, separate `thought` parts) only. flash-lite and Groq's qwen3.8-27b return no reasoning trace regardless of request — no mechanism check possible on those two.
