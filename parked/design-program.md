# Research Program: Evaluating AI-Generated Design Quality

## What this is

A multi-paper research program studying **where AI-generated designs diverge from
high-quality human designs**, across domains (websites, iOS apps, dashboards,
slide decks) and across linguistic/scriptural contexts.

This is **research, not a product**. There is no design checker product, linter,
or tool to ship. Deliverables are papers, datasets, and methodology. (An
automated checker is built as *instrumentation* for paper 1 — it is a
measurement instrument, not the contribution.)

Program-level question:

> When AI systems generate designs, *which* specific principles do they fail to
> follow, and can those failures be measured reliably?

## Paper 1 (current focus)

**Working title:** Japanese typographic conformance in AI-generated web pages,
and whether prompting fixes it.

**Question:** Do frontier and local models generate HTML/CSS that conforms to
documented Japanese text-layout requirements, and how much does prompting —
language, explicit instruction, delivery channel, agentic vs. one-shot — change
that?

### Why this framing (do not re-litigate without cause)

Two earlier framings were considered and deliberately rejected:

- **"AI is worse at Japanese *design conventions*."** Rejected. There is no
  single Japanese design convention; the dense corporate/EC tradition and the
  minimalist tradition give opposite predictions, Japanese startups routinely
  ship Western-style landing pages, and usability principles do not cleanly
  partition by culture. Defending this would mean defending a normative claim
  with no clean source. It also required design expertise and expert
  collaborators that are not available.
- **Pure "how prompting changes AI design."** Rejected as a standalone. The
  dependent variable would be subjective design quality, judged with no design
  expertise, no expert raters, and no participant budget. "Better prompts
  produce better output" is also not a surprising result.

The merged framing keeps the prompting question as the independent variable but
attaches it to an outcome with **objective ground truth in published
standards** — W3C JLReq (Requirements for Japanese Text Layout) and JIS X 4051.
Line-breaking that violates 禁則処理, a font stack with no Japanese-capable
family, `word-break: break-all` shredding a paragraph, a missing or wrong `lang`
attribute: these are *incorrect*, not stylistically different. That is what
makes the paper falsifiable without experts.

### Hypotheses

- **H1 — Baseline conformance.** Models produce Japanese pages with measurable
  typographic/rendering violations at a nontrivial rate.
- **H2 — Prompt-language effect.** Conformance differs when the prompt is in
  Japanese vs. English, holding the target page constant.
- **H3 — Instruction effect.** Explicit standards instruction ("follow JLReq /
  apply 禁則処理") improves conformance, and the size of that effect indicates
  whether the failure is capability or defaulting.
- **H4 — Delivery-channel effect.** The same instruction text delivered through
  a persistent channel (Claude skill, Codex `AGENTS.md`, local system prompt)
  differs from the same text inline in the user turn.
- **H5 — Agentic effect.** Agentic generation (tool use, self-iteration)
  differs from one-shot chat generation.

A null result on any of these is reportable and worth publishing. If models are
largely conformant, that is a genuine finding and a real rebuttal to the
project's own starting assumption.

### Factors

Within-item design: the same page specification is generated under every cell.

| Factor | Levels |
| --- | --- |
| Prompt language | Japanese / English |
| Standards instruction | absent / present |
| Delivery channel | inline user turn / persistent channel |
| Generation mode | one-shot chat / agentic |
| Model | see arms below |

Not all cells exist in all arms (e.g. no agentic mode for plain chat products).
Report the realized design honestly rather than pretending it is fully crossed.

### Arms

1. **Product arm (ecological).** Claude via subscription; ChatGPT and Gemini via
   free tiers. Hidden system prompts and undisclosed context mean this measures
   *deployed products*, not raw models. State this explicitly — do not let a
   reviewer say it first.
2. **Agentic arm.** Claude Code and Codex. Persistent-instruction mechanisms
   (skills, `AGENTS.md`) instantiate the delivery-channel factor here.
3. **Local arm (controlled).** Locally run open models on a 4060 Ti. **Not a
   weaker substitute for frontier models — the control condition.** Fixed seed,
   fixed temperature, fully known context, unlimited samples, zero cost. If the
   prompt effects replicate here, they are not artifacts of hidden system
   prompts. Include at least one Japanese-tuned open model; this cheaply
   pre-empts the predictable "why no Japanese-developed models" objection.
   VRAM caps model size — report the constraint, do not hide it. Verify what
   open models are current at implementation time rather than relying on a
   list written in advance.

Scope guard: the local arm is a **secondary robustness check**. If it starts
tripling the work, cut its factor coverage before cutting the product arm.

## Measurement

**Fully automated. No human raters in paper 1.** This is a deliberate scope
decision: it removes IRB, recruitment, compensation, and the expert-collaborator
dependency, and makes the paper shippable alone.

Instrument: render generated HTML/CSS in headless Chromium (Playwright), then
check computed styles and actual line-box geometry. Candidate checks, each
traced to a clause in JLReq or JIS X 4051:

- Font stack includes a Japanese-capable family; fallback behavior under
  controlled font availability
- Line-break positions vs. kinsoku rules (no leading 。、」）; no trailing 「（)
- `line-break`, `word-break`, `overflow-wrap` values appropriate for Japanese
- Full-width / half-width handling; mixed kanji-kana-latin spacing
- `lang` attribute presence and correctness; `html[lang]` vs. inline spans
- Line-height and measure appropriate for CJK vs. copied Latin defaults

**Requirements for the instrument:**

- Every check cites its source clause. A check with no citation is an ad-hoc
  rubric item and must be dropped or justified separately.
- The checker is validated against a hand-labeled sample before use. Report its
  agreement with manual labeling — this is the automated analogue of inter-rater
  reliability and reviewers will ask for it.
- Checks are versioned alongside the data.

## Methodological commitments

1. **Preregistration.** OSF preregistration before data collection. Cheap, and
   it converts "student compared some models" into a preregistered study.
2. **Within-item design.** Same page spec across all conditions; report effect
   sizes rather than chasing significance at small N.
3. **Instrument validation.** As above — checker vs. hand labels.
4. **Reproducibility.** Model names are moving targets. Date-stamp every model
   ID and label, log every full prompt, temperature and seed where available,
   and note where they are *not* available (chat products). Archive raw outputs
   verbatim. The dataset is likely the most reused output of this work.
5. **Chat-product limitations stated up front.** No temperature control, no
   seed, unknown and changing system prompts, hidden conversation state.
   Mitigation: one fresh conversation per generation, everything logged.
6. **Analysis.** Mixed-effects models with random intercepts for page spec and
   model. Power/sample decisions made before collection.
7. **Confound discipline.** Agentic vs. one-shot is a *factor*, never noise.
   Delivery channel is defined operationally (identical instruction text,
   different mechanism), not by platform-specific feature names.

## Constraints (real, shape everything)

- Student, no budget, no institutional resources assumed
- No design training; **bilingual Japanese/English** — this is the enabling
  asset for this specific paper and the reason it is the right first paper
- No confirmed expert collaborators; the design is built to not require them
- No hard deadline — so scope discipline must come from somewhere else
  (preregistration and a named target venue)
- Local compute: single 4060 Ti; caps local models to small quantized ones

## Later papers (the series, not paper 1)

Do not pull these forward.

- Other domains: iOS, dashboards, slide decks
- Other scripts with documented layout requirements (Korean, Arabic, Thai,
  Devanagari) — the JLReq approach generalizes to any language with a
  standards body
- Human-rated aesthetic/usability quality, once expert collaborators exist
- Cultural convention questions, only if a defensible construct can be built

## Outputs and publication order

1. Technical paper, stabilized
2. arXiv preprint
3. Medium article (general audience, English)
4. note article (Japanese)
5. Public GitHub repo: checker, prompts, page specs, raw outputs, analysis code

The popular versions will be read by people who scrutinize the claims closely.
The technical version should exist first.

**Venue:** name one early and work backward — CHI Late-Breaking Work, IUI, CSCW
posters; WISS or IPSJ HCI研究会 for the localized version.

## Writing conventions

- **No "AI slop"** or similar rhetoric in the paper. Neutral framing
  ("conformance to documented layout requirements"). Informal framing is
  acceptable in the Medium piece only.
- Claims are about specific measured checks, never about design being globally
  "worse."
- Report negative and null results, including conditions where models conform
  fully.
- Do not make claims about Japanese design *taste* or *convention*. That is
  explicitly out of scope for paper 1.

## Open decisions

- [ ] Target venue (no deadline exists, so this substitutes for one)
- [ ] Final check list, each mapped to a JLReq / JIS X 4051 clause
- [ ] Page-spec set: how many, which genres, how specified
- [ ] Model set per arm; which Japanese-tuned open model
- [ ] Which persistent-instruction mechanisms count as the same channel
- [ ] Whether agentic arm includes Codex, and whether Antigravity is reachable
- [ ] Sample size per cell; hand-labeled validation set size
- [ ] Whether any supplementary human rating is worth adding after the automated
      result exists

## Repository conventions

- Working directory: `/Users/rios/research` (not yet a git repository — should
  become one before any data collection)
- Raw model outputs archived verbatim, never edited in place
- Prompts, page specs, checker, and analysis code versioned alongside the data
- Every archived generation records: model label, date, arm, all factor levels,
  full prompt text, and any available sampling parameters
