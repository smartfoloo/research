# Research Project: Closing the Non-English Gap in LLM Code Generation

## How to work with me on this

**Act as a research advisor, not an implementing agent.** Critique framing,
surface threats to validity, propose structure, point at literature. Do not
write the experiment code, the analysis, or the paper unless explicitly asked.
The value of this project is in doing it myself; work produced for me is work I
cannot defend.

Do not start responses with praise. Be direct about problems. If a framing is
weak, say so and say why.

## Status

**Topic settled 2026-08-04.** Three earlier framings were abandoned; this one is
committed. The pivot budget is spent.

**2026-09-06 — presentation deadline (2 days from 2026-09-05), spike scoped
down to fit it.** A presentation is due showing in-progress, non-final
results — explicitly **not** required to be fully accurate or the final
research result. This does not change the paper's eventual rigor bar (still
preregister before the real study, still needs the full arms/budget/N
eventually) — it only changes what the *next 48 hours* optimize for: a
working pipeline and real (if small/preliminary) numbers, not statistical
power or completeness. Deviations from the original spike design, all
reversible for the real study later:
- Task count: 10 → **6** (3 simple, 3 complex) — see task list below
- Samples per cell: 5 → **3**
- Local models: primary run is **`qwen3.5:9b` only**; `deepseek-r1:14b` and
  `gemma4:12b` are bonus-only if time remains (both are "tight fit" on 8GB
  VRAM per CanIRun.ai — slower, don't let them block the deadline)
- All 6 tasks now have all 4 conditions (en_human, ja_raw, ja_directive,
  mt_en) fully authored and filled into `spike/prompts.json` — pipeline is
  unblocked, ready to run

**2026-09-06 — spike run, bugs found and fixed, results in.** Full pipeline
run on real hardware surfaced 5 real bugs before any result could be trusted
(grading silently collapsed to 1 of 72 files via a pathlib bug; an f-string
quote collision crashed the test script for any string-valued expected
output; Windows subprocess decoding used cp1252 and crashed on non-ASCII
model output, taking the whole batch down with it; naive join-all-fenced-
code-blocks extraction let a broken revision silently override a correct
one; Ollama's 4096-token default context silently truncated 61% of
`ja_directive` generations before any answer was written). All fixed and
verified. `business-days`'s English/Japanese wording ("Ignore holidays")
turned out ambiguous — it invited unrequested holiday-exclusion logic that
then had bugs in it — revised to "Don't account for holidays, calculate
strictly based on day of the week" (both languages) and regenerated.

N doubled 3→6/cell after the initial N=3 run showed `en_human` as the worst
condition (looked backwards for H1) — turned out to be small-N noise: manual
inspection of all 10 `en_human` failures found generic coding mistakes
(over-engineering, typos, misreads), not English-comprehension problems. At
N=6 the picture is sane again: en_human 67%, ja_raw 64%, **ja_directive 94%**,
mt_en 53% (now the worst condition — 0/6 on both currency-format and
eval-expression, not yet dug into). ja_directive's mechanism is confirmed,
not assumed: reasoning-trace language check shows ja_raw is mixed
(10/18 majority-Japanese), ja_directive is 18/18 majority-English — but it
costs ~3x the output tokens of every other condition, and — open question,
not yet resolved — en_human's trace is *also* ~100% English without getting
the same boost or the same token cost, so "reasoning in English" alone
doesn't explain the ja_directive/en_human gap. Leading hypothesis: the
directive functions as a generic deliberation trigger (more test-time
compute), with the English-ness being incidental to this model rather than
causal. Untested control that would settle it: a same-language ("think
carefully, Japanese, no language switch") directive.

Also ran a second model, **`gemma-4-31b-it` via Google AI Studio** (free
tier: 30 RPM / 16K TPM / 14.4K RPD) — not the planned Claude/OpenAI frontier
arm, just a free, fast way to sanity-check the ceiling-effect risk this
document already flagged below. It hit exactly that: 97-100% pass rate in
every condition, 2 failures out of 144 generations total, task set is too
easy for this model to show any language effect at all. But token cost
still differentiates conditions even at ceiling: ja_directive costs Gemma
only ~1.2-1.3x the other conditions (vs qwen3.5's ~3x), and unlike qwen3.5,
Gemma's *thinking*-token count barely moves across conditions (704-804,
flat) — the extra cost shows up in a longer final answer, not more
deliberation. Consistent with: a weak/quantized model needs (and pays for)
real extra deliberation to close a real gap; a strong model has no gap to
close and pays little either way. Scripts are fully separate from the local
arm (`spike/arms/gemma/generate.py`, `spike/arms/gemma/grade.py`,
API key in a gitignored file, never committed) — zero risk to the Ollama
pipeline.

Discussed but not yet built: one very complex, still single-file,
still-abstract/algorithmic bonus task (e.g. a small expression-language
interpreter with variables/functions/recursion) specifically to get a
stronger model like Gemma off its ceiling. Flagged risks before building it:
(1) N=6 on one task is exactly as fragile as the N=3 problem above, just
concentrated on one data point instead of averaged over six; (2) prompt-
equivalence risk (see business-days above) scales with task complexity, not
just difficulty; (3) doing it properly costs the same authoring/verification
effort as any of the existing 6 tasks. Treat as one labeled exploratory
bonus task if built, not a claim-bearing addition to the main 6-task result.

**2026-09-07 — parked/ removed from the repo.** A parked program on evaluating
AI-generated *design* quality (Japanese typographic conformance, JLReq-based)
previously lived at `parked/design-program.md`. Deleted during a repo cleanup
(it is recoverable from git history if revived) — it was not dead and not
scooped, just not being worked on; that hasn't changed, only its presence in
this repo has.

**2026-09-07 — en_human/ja_raw backtick-formatting inconsistency found and
fixed, with a reproducibility caveat.** Auditing `prompts.json` vs
`prompts-bonus.md` for formatting drift (prompted by adding the 2 bonus
tasks) surfaced that `en_human` was plain text while `ja_raw`/`ja_directive`
used backtick-formatted identifiers/values in 5 of the 6 core tasks — a
typographic prompt-equivalence gap, lower-severity than a wording/structure
mismatch but still exactly what Method 3.2 gets checked for. Fixed by adding
matching backticks to `en_human` for those 5 tasks (not `business-days`,
which is plain in both EN and JA already — left alone) and both bonus
tasks, rather than stripping backticks from `ja_raw` — English competitive-
programming prompts (LeetCode/HackerRank-style) commonly backtick-format
identifiers too, so this brings `en_human` in line with realistic register
rather than making it artificial.

**Reproducibility caveat this creates:** the 5 affected core tasks'
`en_human` text already produced 144 real, graded samples (36 × 4 arms —
qwen3.5, gemma, flash-lite, groq) whose pass rates are published in
`RESULTS.md`. Those generations were made against the *old* (non-backtick)
`en_human` text. `prompts.json` no longer matches the text that actually
produced those numbers. The raw data stays internally honest — every
generation file's `_meta.prompt_text` records exactly what was sent — but
re-running the pipeline from current `prompts.json` will not reproduce
`RESULTS.md`'s exact `en_human` numbers until/unless those samples are
regenerated. Not regenerated as part of this fix (144 samples, free-tier
API time, not obviously worth it for spike-stage results already superseded
by the real study's protocol) — flagging so this isn't rediscovered as a
mystery later. Real study must not carry this forward: freeze prompt text
formatting before any generation happens, not after.

## The question

> Non-English speakers get measurably worse code generation from the same models
> on the same tasks. **Which interventions close that gap, and what do they
> cost?**

This is deliberately *not* "which language is cheaper to prompt in." That
question is answered (English), and the answer is only actionable by bilinguals.

### Framing

Prompt language is usually **not a free choice**. It is determined by the
developer's language, their team, their specification, their documentation. The
population of interest is **monolingual Japanese developers**, who cannot act on
the advice "just prompt in English."

So the intervention space is not *which language to choose* but *what to do with
a Japanese prompt you already have.*

### Conditions (the interventions)

Same task, four pipelines:

| Condition | Description | Available to a monolingual? |
| --- | --- | --- |
| **JA-raw** | Native Japanese prompt, sent as-is | yes — the status quo |
| **JA+directive** | Japanese prompt + explicit "reason/think in English" instruction | yes |
| **MT-EN** | Japanese prompt machine-translated to English, then sent | yes |
| **EN-human** | Human-written English prompt | **no** — upper-bound baseline only |

EN-human is the ceiling, not a recommendation. The paper's value is in whether
JA+directive or MT-EN recovers most of the distance to it, and at what cost.

**Resolved (was ambiguous, flagged 2026-09-05):** the directive itself must be
written **in Japanese**, not English — otherwise "available to a monolingual"
in the table above is false, since a monolingual couldn't add an English
sentence to their own prompt. Directive text used: 英語で考えてから回答してください。
("please think in English before answering"), same sentence appended to every
task's ja_raw text, unedited beyond that append. MT-EN direction is **JA→EN**
only — the population (monolingual Japanese developers) has no English
original to translate from; there is no ja-from-en path anywhere in the
pipeline. MT system used: Google Translate (translate.google.com), raw/verbatim
output, not polished — see Threats to Validity.

## Positioning against prior work

Read and cite all of these. Verify citations directly; some were recalled from
memory.

- **Ren et al. (arXiv 2604.14210, Apr 2026),** *"Chinese Language Is Not More
  Efficient Than English in Vibe Coding."* 3 model families, 50 SWE-bench Lite
  tasks. English wins on solve rate; Chinese token savings marginal or reversed;
  tokenizer training data, not linguistic properties, is the determinant.
  **This paper measures the gap. It does not test interventions against it.**
  That distinction is this project's entire contribution — state it explicitly
  in the introduction.
- **Multilingual reasoning-trace work.** arXiv 2508.14828 (*Long Chain-of-Thought
  Reasoning Across Languages*), arXiv 2601.02996 (*Large Reasoning Models Are
  (Not Yet) Multilingual Latent Reasoners*), arXiv 2210.03057 (*Language Models
  are Multilingual Chain-of-Thought Reasoners*). The "quote-and-think" pattern —
  reason in English, answer in the prompt language — is already published. Do
  not claim it. Use it as the mechanistic justification for the JA+directive
  condition.
- **Tokenizer fairness:** Petrov et al. and Ahia et al. (~2023). The input-side
  language tax is established; cite it, do not re-derive it.
- **Translate-test.** Translating input to English before inference is a
  long-standing multilingual NLP paradigm. Reviewers will know it. **The
  technique is not the contribution** — measuring it for code generation, with
  both correctness and full cost accounting, against JA+directive as an
  alternative, is.

### Must verify before committing further

- [ ] Forward citations of Ren et al.
- [ ] Translate-test applied specifically to **code generation** — if this exists
      with cost accounting, this framing closes too
- [ ] Recent arXiv cs.CL and cs.SE for Japanese/multilingual code-gen work
- [ ] Existing Japanese-translated variants of coding benchmarks

**Process lesson from the last pivot: literature search precedes framing.**

## Hypotheses

- **H1 — Gap exists.** JA-raw has a lower pass rate than EN-human on identical
  tasks. (Replication of Ren et al. in Japanese. If this fails, there is no
  paper — see the spike.)
- **H2 — Directive helps.** JA+directive recovers part of the gap by inducing
  English reasoning, at low token cost.
- **H3 — Translation helps more.** MT-EN recovers more of the gap than
  JA+directive, but adds translation overhead (tokens, latency, or an external
  dependency).
- **H4 — Cost ordering.** Total cost per *correct* solution differs across the
  four conditions, and the ordering is not the same as the ordering by raw token
  count.
- **H5 — Complexity interaction.** The gap and the interventions' effectiveness
  differ between simple and complex tasks.

Null results are reportable. "Neither intervention closes the gap" is a real
finding with real implications.

## Metrics

- **Primary: correctness.** Unit tests passing; pass@k with k fixed in advance.
  The gap is a correctness gap first — cost is the secondary story. This is a
  change from the earlier cost-centric framing and is deliberate.
- **Secondary: raw token counts** — input, output, and reasoning tokens reported
  separately, never collapsed.
- **Derived: dollar cost**, from published rates with the retrieval date
  recorded. Derived rather than measured, because prompt caching changes billed
  cost without changing token counts; a cost-primary study would be an artifact
  of cache-hit patterns and would not reproduce.
- **Mechanistic: reasoning-trace language**, to verify the directive actually
  works. Visible on the local arm; token counts only on hosted APIs.
- **Overhead:** translation cost for MT-EN (tokens and/or API calls), and
  latency.

## Design and arms

Within-item: the same task runs under every condition.

| Factor | Levels |
| --- | --- |
| Condition | JA-raw / JA+directive / MT-EN / EN-human |
| Task complexity | simple / complex (operationalization TBD) |
| Reasoning mode | off / on, where supported |
| Model | see arms |

1. **Local arm (primary).** Open models on a 4060 Ti. Exact token accounting,
   fixed seed and temperature, visible reasoning traces, unlimited samples, zero
   cost. Develop and finalize the entire protocol here. VRAM caps model size —
   report the constraint.
2. **Frontier arm (ecological, secondary).** Claude and OpenAI via API. Hard
   budget **~$20 per provider**. API only — chat subscriptions give no token
   accounting, no seed, no temperature control.

## Budget discipline

- **Spend frontier budget last**, once, on the final protocol. A pilot on a
  design that later changes leaves nothing and no way to replace it.
- **Derive N empirically:** run ~10 real samples, read actual billed usage,
  compute cost per sample, then N = budget ÷ cost. Reasoning modes cost far
  more; pass@k multiplies everything by k.
- **Investigate batch endpoints** (discounted; no deadline means latency is
  free) **and prompt caching** (task prompts recur across conditions).
- **Never take pricing from Claude.** Pull from provider pricing pages and
  record the retrieval date.

## Threats to validity

- **Prompt equivalence — the central one.** Bad translations look exactly like
  language effects. Author the Japanese personally, verify by back-translation,
  ideally get a second bilingual reader.
- **Translationese trap.** If the Japanese prompts are produced by translating
  English benchmark prompts, they are already translationese, and MT-EN may
  recover the English original almost exactly — inflating the MT condition
  against a real-world scenario where the Japanese was written natively. Either
  source natively-written Japanese task descriptions, or state this limitation
  explicitly and prominently.
- **MT system is a confound.** Record which MT system and version; results are
  conditional on it. Consider more than one.
- **Directive compliance.** Verify the model actually reasons in English when
  told to; do not assume. This is measurable on the local arm.
- **What varies with language.** Task description only? Code comments?
  Identifier names? Each has different token and correctness consequences.
  Control or factor explicitly.
- **Task construct assumes a language-specific structure.** Distinct from the
  above: does the *task itself*, not just its description, depend on a
  feature one language has and the other doesn't? Example caught in the spike
  (2026-09-01): "reverse the words in this sentence" assumes whitespace word
  boundaries, which Japanese lacks — the JA version would secretly test word
  segmentation, the EN version wouldn't. Audit every task for this before
  finalizing; prefer abstract/structured inputs (arrays, graphs, numbers) over
  raw natural-language processing where the task allows it.
- **Benchmark contamination.** HumanEval/MBPP are heavily contaminated. Check
  existing Japanese variants; known quality issues.
- **Model versions move.** Date-stamp every model ID; log temperature, seed, and
  all sampling parameters.

## Step 0 — tokenizer measurement (do this first, costs nothing)

Before any model inference. Pure measurement, no hypothesis, no budget.

**What:** tokenize the paired Japanese/English coding prompts across several
tokenizers (tiktoken for OpenAI, HuggingFace tokenizers for open models,
Anthropic's token-counting endpoint) and report the JA/EN token ratio.

**Why do it now:**
- Zero cost, no API credits, no inference.
- It requires authoring the paired prompt set — which the spike needs anyway.
- It grounds H1 with a concrete number instead of a citation.

**This is not the experiment.** Token counting is a descriptive statistic anyone
can compute; a paper contributing only that would be rejected, and the answer is
largely predictable from Petrov et al. and Ahia et al. It belongs in the paper
as a preliminary measurement (Section 4.1), not as the contribution.

**The one genuinely open thing here:** coding prompts are unusual text — full of
identifiers, code snippets, numbers, ASCII, and English technical vocabulary
that tokenizes identically in both languages. A Japanese *coding* prompt may be
far less Japanese-dense than general prose, so the ratio could be substantially
lower than the general-text figures in the tokenizer-fairness literature. That
appears unreported. Worth a subsection; not worth a paper.

**Caveat:** the ratio is a property of *your prompts*. Verbose Japanese against
terse English inflates it artificially. Report character counts and the
back-translation verification alongside the token ratio.

## Feasibility spike — do this after step 0

One to two days. The go/no-go for the whole project.

**The decisive question: does the correctness gap reproduce on my setup?**
Everything depends on H1. If Japanese prompts don't underperform on small local
models and the tasks available, there is nothing to close and the project stops.

**Setup (as actually run, 2026-09-06):** 6 original tasks (not from an existing
benchmark — self-authored, see task list below), 3 simple / 3 complex. Japanese
prompts authored by the researcher (bilingual), calibrated against AtCoder/
Qiita register, not yet back-translation-verified by a second reader (cut for
the 2-day deadline, flag as a limitation on this round). Primary model:
`qwen3.5:9b` (visible reasoning trace). All four conditions, all 6 tasks, fully
authored. 3 samples per task per condition (reduced from 5 for time).

**The 6 tasks:**
- Simple: business-days, currency-format, reverse-list-elements
- Complex: eval-expression, shortest-path, bank-rollback
(Originally 10 — dedupe-sort, valid-email, lru-ttl-cache, meeting-rooms cut for
ceiling risk / redundancy / reduced grading scope. Full 10 still in
`spike/task-specs-en.md` if useful for the real study later.)

**Record per sample:** condition, pass/fail, input/output/reasoning tokens,
language of the reasoning trace.

**Decision rules:**

- **Clear JA-raw deficit, and either intervention narrows it** → proceed as
  planned.
- **Clear deficit, neither intervention helps** → still a paper, reframed as a
  negative result about intervention ineffectiveness. Weaker but real.
- **No deficit at all** → H1 fails on this setup. Check whether it's the model
  scale, the task difficulty, or the benchmark before abandoning; small local
  models may be too weak for a gap to be visible. Consider spending a little
  frontier budget to test whether the gap exists there before concluding.

**Floor/ceiling effects — check per arm, not just per H1 overall.** The local
and frontier arms sit at very different absolute capability levels by design
(that's fine — arms are never compared to each other on raw pass rate, only
within-model across conditions). But each arm needs task difficulty in the
range where the model can *sometimes* fail, in every condition, or no gap can
be visible regardless of whether one exists:
- **Floor effect (local arm):** models too weak, ~0% pass rate everywhere
  regardless of condition. No room for a gap to show.
- **Ceiling effect (frontier arm) — same failure, opposite direction:**
  models strong enough to pass ~100% on the simple tasks especially,
  regardless of prompt language. No room for a gap to show either.
Look at per-arm pass rates after the spike before interpreting a null result
as "no gap exists" — it may mean "this task set can't show one in this arm."
If frontier saturates near 100%, the complex 5 tasks may need to get harder
specifically for that arm; don't assume the same difficulty band works for
both arms just because it's the same task set.

**Confirmed, not just anticipated (2026-09-06):** ran `gemma-4-31b-it` (a
stronger model than qwen3.5:9b, via Google AI Studio's free tier, not the
planned frontier arm) against the same 6-task set — 97-100% pass rate in
every condition, 2 failures out of 144. Textbook ceiling effect exactly as
predicted above. Confirms this task set cannot test H1-H5 on models much
stronger than qwen3.5:9b without harder tasks — see the bonus-task note in
Status above.

Preregistration comes *after* the spike.

## Paper structure (draft)

First paper — so each section below says what it is *for*, not just what goes in
it. Write Method and Results first; Introduction last (you can't introduce a
result you don't have yet).

### Abstract
~200 words: problem, what you did, what you found, why it matters. Written last.
Most readers read only this — it must contain your actual numbers, not a promise
of numbers.

### 1. Introduction
Answers "why should I care?" and "what's new?" Standard four moves:
1. Non-English developers get worse code from the same models.
2. Prior work measured this gap but only offers advice ("prompt in English")
   that monolingual developers cannot use.
3. So: which usable interventions actually close it, and what do they cost?
4. Contributions, as a bulleted list. Be specific and modest — claim only what
   your data supports.

The last paragraph should tell the reader exactly what they'll learn.

### 2. Background / Related Work
Shows you know the field and, critically, **positions your work against it**.
Not a book report — every paper cited should end with "…but they did not X,"
where X is what you do.

- 2.1 Tokenizer fairness and the language tax
- 2.2 Multilingual code generation and the solve-rate gap (Ren et al.)
- 2.3 Reasoning-trace language and quote-and-think
- 2.4 Translate-test in multilingual NLP

Reviewers check this section to see whether you've been scooped. Address Ren et
al. head-on rather than hoping nobody notices.

### 3. Method
The reproducibility contract: enough detail that a stranger could rerun this and
get your numbers. Written in past tense, describing what you *did*, not what one
*could* do. When in doubt, over-specify — model IDs with dates, temperature,
seeds, prompt text.

- 3.1 Task set and complexity levels
- 3.2 Prompt authoring and equivalence verification — how you know the Japanese
  and English prompts say the same thing. This is the section a skeptical
  reviewer attacks first.
- 3.3 The four conditions
- 3.4 Arms, logging, reproducibility

### 4. Results
**Findings only — no interpretation.** "JA-raw passed 61% vs 78% for EN-human"
belongs here; "this suggests tokenizer bias" belongs in Discussion. Beginners
mix these constantly and reviewers always notice.

One subsection per hypothesis, in hypothesis order, so a reader can check you
answered each one:

- 4.1 The gap in Japanese (H1)
- 4.2 Reason-in-English directive (H2)
- 4.3 Machine translation (H3)
- 4.4 Cost per correct solution across conditions (H4)
- 4.5 Complexity interaction (H5)
- 4.6 Reasoning-trace language as mechanism
- 4.7 Local vs. frontier

Report effect sizes, not just "significant." Report null results with the same
prominence as positive ones. Every table and figure needs a caption that stands
alone.

### 5. Discussion
What the numbers *mean*, and the practical payoff: **what a Japanese developer
should actually do.** Also why you got the result you got — connect back to the
mechanism (quote-and-think, tokenizer training data). Speculation is allowed
here, but label it as speculation.

### 6. Limitations
Every honest paper has one. Naming your own weaknesses pre-empts reviewers and
signals competence; hiding them reads as naivety. Yours will include: small
local models, one language pair, single MT system, benchmark contamination, the
translationese trap, chat-product opacity. State each plainly, and say what it
does and does not threaten.

### 7. Conclusion
Short. Restate the finding and one sentence of what's next. No new information.

### Appendices
Prompt sets, task list, full token logs — everything a replicator needs that
would clutter the main text.

## Constraints

- Student; first research project; no institutional resources assumed
- Budget: ~$20 per provider (Claude, OpenAI)
- Local compute: single 4060 Ti — small quantized models only
- Bilingual Japanese/English — the enabling asset for prompt authoring
- No hard deadline, so scope discipline comes from the spike, a named venue, and
  preregistration

**Realistic ceiling: a strong workshop or short paper.** The interventions are
not novel techniques; the measurement in this setting is the contribution.
Aiming there deliberately is the right call for a first project — a finished
workshop paper beats an unfinished full one.

## Later papers / future work (not paper 1)

**Domain generalization.** Paper 1's spike and study use pure algorithmic,
unit-testable tasks only (string/data-structure/algorithm problems) — a single
domain with one cheap, uniform, automatable correctness check (pass/fail unit
tests). Do not pull other domains into paper 1: web app tasks, iOS app tasks,
and Ubuntu server/sysadmin config tasks each require a **different evaluation
harness** (browser automation + DOM assertions; Xcode/simulator build-and-run,
which needs a Mac; disposable VM/container state-checking), not just "harder
code." Mixing them into one study would vary the evaluation method alongside
the language condition, confounding "no gap found" with "my harness is broken."

Once the four-condition method (JA-raw / JA+directive / MT-EN / EN-human) is
validated on the algorithmic domain, generalizing it to web/iOS/sysadmin tasks
is a strong **second paper** — same logic as the parked design program's
domain list.

## Venue

NLP/SE, not CHI. Candidates: ACL/EMNLP workshops (multilinguality, efficient
NLP), MSR, or an SE workshop. Name one and work backward from its deadline.

## Open decisions

- [ ] Target venue and deadline (still open for the *paper*; the 2026-09-06
      presentation deadline above is separate and already resolved)
- [ ] Benchmark and task set for the **real study** — spike used 6
      self-authored tasks, not an existing benchmark; still worth checking
      existing Japanese-translated benchmark variants before finalizing
- [x] Whether task descriptions can be sourced natively in Japanese — spike
      used researcher-authored JA, not translated from EN; back-translation
      verification by a second reader still outstanding (cut for time)
- [x] Operationalization of simple vs. complex — 3 tasks each, see task list
      in the spike section
- [x] Exact wording of the reason-in-English directive — 英語で考えてから回答してください。
- [x] MT system(s) — Google Translate (translate.google.com), JA→EN, one
      system only so far
- [x] Local model set for the spike — `qwen3.5:9b` primary (Q4_K_M
      quantization, GGUF, confirmed via `ollama show`; native context
      262144, spike configured num_ctx up to 32768 — inconsistently across
      the run, see below). `deepseek-r1:14b`/`gemma4:12b` never run
      (bonus-only, deprioritized once qwen3.5 showed a usable signal).
- [x] Ad hoc second model, not the planned frontier arm — `gemma-4-31b-it`
      via Google AI Studio free tier, run for real (144 generations, graded).
      Hit a ceiling effect (97-100% pass rate) — see Status above. Real
      study still wants Claude/OpenAI as the actual frontier arm per the
      $20/provider budget plan; Gemma was zero-cost exploration, not that.
- [ ] Frontier model set (Claude/OpenAI) and reasoning coverage within
      budget — not touched yet, budget still fully unspent
- [x] Samples per cell for the spike — bumped 3→6 mid-run (see Status) after
      N=3 produced a result (en_human worst) that didn't survive doubling.
      Real-study N still needs deriving properly per Budget discipline above,
      this was reactive, not planned.
- [ ] pass@k value — not yet decided, spike is just recording raw pass/fail
- [ ] Sampling params were not fixed or logged during the spike run itself —
      recovered after the fact via `ollama show` (qwen3.5:9b ships with
      temperature=1, top_k=20, top_p=0.95, presence_penalty=1.5, never
      overridden) and Google's model-info endpoint (gemma-4-31b-it defaults
      to temperature=1, topP=0.95, topK=64). Real study must set and record
      these explicitly per generation, not reconstruct them after the fact.
- [ ] `num_ctx` was not held constant across the qwen3.5 spike dataset —
      early files used Ollama's 4096 default (before the truncation bug was
      caught), most used 16384, 2 outlier regenerations used 32768. Doesn't
      currently affect any result (nothing hit a lower ceiling after the
      fixes), but real study should fix one value up front and log it.
- [ ] Bonus complex single-file task (e.g. expression-interpreter-with-
      variables) to get a stronger model off its ceiling — discussed
      2026-09-06, not yet built, see Status above for the risks flagged
      before starting it.

## Repository conventions

- Working directory: `/Users/rios/research` — git repo initialized 2026-09-05,
  branch `main`, pushed to GitHub (smartfoloo/research, private)
- Raw model outputs archived verbatim, never edited in place
- Prompts, task sets, and analysis code versioned alongside the data
- Every generation records: model label, date, arm, condition, all factor
  levels, full prompt text, all sampling parameters, full token accounting
- Pipeline (reorganized 2026-09-07 for navigability — one folder per model
  arm, same two-file shape in each):
  - `spike/arms/qwen3_5_local/` — `generate.py` (Ollama → raw JSON per
    generation, resumable, skips completed/missing) → `grade.py` (Docker,
    isolated, network-disabled → pass/fail per generation)
  - `spike/arms/gemma/`, `spike/arms/flash_lite/`, `spike/arms/groq_qwen3_8/`
    — same `generate.py`/`grade.py` shape, one per hosted-API arm
  - `spike/grading_common.py` — extraction/harness/sandbox logic shared by
    all four arms' `grade.py` (a fix here applies everywhere at once)
  - `spike/test_cases.py`, `spike/prompts.json` — shared across all arms
  - `data/raw/<arm>/` — one raw+grade JSON pair per generation, per arm
    (`qwen3_5_local/`, `gemma/`, `flash_lite/`, `groq_qwen3_8/`)
  - `data/analysis/` — one-off ad hoc scripts (chart tables, token usage,
    manual failure inspection); not part of the live pipeline
  - `data/logs/` — saved stdout from past generation/grading runs
  - `RESULTS.md` (repo root) — current pass-rate/token-cost tables, all arms
  - Ollama's `/api/generate` response includes `prompt_eval_count`/
    `eval_count` (input/output tokens) automatically — captured for free, no
    extra instrumentation needed. Whether reasoning-trace tokens are
    separated from answer tokens in the response, or bundled together (e.g.
    inside `<think>...</think>` in the text), is unverified — check the
    first real `qwen3.5:9b` output before trusting any reasoning-token
    breakdown.
