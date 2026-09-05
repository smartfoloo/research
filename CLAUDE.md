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
committed. The pivot budget is spent. Next commitments: the verification
searches, then the feasibility spike, then preregistration.

A parked program on evaluating AI-generated *design* quality (Japanese
typographic conformance, JLReq-based) lives at `parked/design-program.md`. It is
not dead and it is not scooped, but it is not being worked on.
`sample-sites-codex/` is leftover material from it.

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

**Setup:** ~10 tasks from an existing benchmark. Japanese prompts authored by
me, back-translation verified. One local reasoning model with a visible trace.
All four conditions. 5 samples per task per condition.

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

- [ ] Target venue and deadline
- [ ] Benchmark and task set; existing Japanese variants
- [ ] Whether task descriptions can be sourced natively in Japanese
      (see translationese trap)
- [ ] Operationalization of simple vs. complex
- [ ] Exact wording of the reason-in-English directive
- [ ] MT system(s)
- [ ] Local model set; which expose reasoning traces
- [ ] Frontier model set and reasoning coverage within budget
- [ ] pass@k value and samples per cell

## Repository conventions

- Working directory: `/Users/rios/research` — **not yet a git repository; make it
  one before any data collection**
- Raw model outputs archived verbatim, never edited in place
- Prompts, task sets, and analysis code versioned alongside the data
- Every generation records: model label, date, arm, condition, all factor
  levels, full prompt text, all sampling parameters, full token accounting
