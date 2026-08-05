# HAS-Core :: SDIR

**Synthetic Data Inbreeding Rate** — a formative-layer read-out for AI training data.

> **License: Non-Commercial Research only.** Free for research and study.
> Commercial use requires prior written permission — see [LICENSE](LICENSE).

> **Scope & status (read first).** SDIR is a **lightweight, minimal
> proof-of-concept**. Its purpose is to demonstrate a *direction*: that the
> integrity of training data can be examined at the **formative layer**, before
> a model trains on it, and to show one way that examination can be made to run.
> It is **not** a production detector and does **not** claim to solve synthetic
> data detection. It is a **read-only** instrument that measures how far a batch
> has drifted from a human baseline you supply, in ways consistent with
> recursive synthesis. It must **not** be used at full training scale, and its
> score must **not** be a standalone gate on a training decision. A diagnosis is
> evidence; a separate policy layer decides. SDIR reports **drift from your
> baseline, not a good/bad verdict**: a batch can drift because it is
> recursively synthesised, or because it is legitimately narrow human text. The
> baseline **must match the batch's domain and language**, or the drift it
> reports will be real but not a defect.
>
> **What this is for.** A robust, engineering-grade implementation is a much
> heavier undertaking (language-model perplexity, semantic-embedding models,
> trained classifiers, and the compute they require). That is deliberately not
> what this is. This release exists to make the direction visible and runnable,
> so its value can be seen. Building the robust version for a specific setting
> is exactly the kind of work a direct collaboration would take on.

> **v1.1 (partial hardening).** After public adversarial review, v1.0's
> multiplicative fusion was found to allow a **false CLEAR**. v1.1 addresses
> part of this: text-intrinsic drift can no longer be vetoed by a single
> signal, provenance is treated conservatively (missing or unknown raises risk,
> never lowers it), and recursion and diversity are measured *relative to the
> baseline* so legitimately homogeneous human text no longer self-flags. The
> **provenance-relabelling** attack is closed by these changes.
>
> **Known boundaries of this minimal version.** In the course of developing and
> testing SDIR, and with the help of independent reviewers, we identified the
> points where a lightweight, purely statistical approach reaches its limit.
> These are stated openly so no one mistakes the demonstration for a robust
> detector. Crossing them is what an engineering-grade implementation, and a
> direct collaboration, would take on:
>
> - **A poisoned baseline can cancel the signals.** Because recursion and
>   diversity are measured relative to the baseline you supply, an equally
>   synthetic baseline can drive them to zero. The reference frame is under the
>   caller's control and is not itself audited here.
> - **Gradual contamination is under-detected.** A batch that is a small
>   fraction synthetic can still read low. Reliably separating light
>   contamination from ordinary narrow human text is beyond what word-frequency
>   statistics alone can do, and needs heavier methods.
> - **Cosmetic edits can evade the text signals.** Rotating openers and adding
>   rare tokens can lower the surface signals while the recursive core is
>   unchanged.
> - **English only.** The vectoriser uses English stop-words and the tokeniser
>   does not segment scripts such as Chinese. This release is scoped to English;
>   do not run it on non-Latin text, where results are not meaningful.
>
> None of these are hidden. They mark the edge of a deliberately minimal tool.
> The direction it points to, examining data integrity at the formative layer,
> is the part meant to carry forward. With sincere thanks to the reviewers whose
> testing sharpened these boundaries.

Part of **HAS-Core**, the open, minimal tier of a formative-layer auditing
framework. Where run-time evaluation (red-teaming, sandboxes, capability tests)
measures *what a model already does*, formative-layer auditing measures the
*internal conditions under which those behaviours become possible* — and it does
so **before** the model trains on the data.

SDIR is the first released protocol. It answers one question a benchmark cannot:

> Is this training batch beginning to feed on itself — collapsing toward a
> narrow set of sources, recursively re-synthesising its own output, and losing
> the long tail of human experience — *before* a single weight is updated?

---

## Why this exists

Modern corpora increasingly contain model-generated text, which is then scraped
back into the next model's training set. Over generations this produces **source
contraction, recursive synthesis, and semantic diversity loss** — "data
inbreeding." Standard accuracy metrics and run-time evals do not see it, because
the text still reads fluently. SDIR reads the *structure* of the batch, not its
fluency, and flags the collapse while it can still be corrected.

---

## Quick start

```bash
git clone <this repo>
cd has-sdir
pip install numpy scipy scikit-learn matplotlib

# see it separate healthy data from inbred data, with a figure:
python demo.py
```

`demo.py` builds three corpora (no downloads) and writes `sdir_demo.png`: a
healthy multi-source batch (reads CLEAR), a recursively-synthesised batch (high
drift), and the *same* recursive batch with its provenance relabelled to look
diverse, which v1.1 still flags where v1.0 could be fooled into CLEAR. This
demonstrates the one attack v1.1 does close; see **Known boundaries of this
minimal version** above for what a lightweight approach does not attempt.

### Run it on your own data

```bash
python run_sdir.py --batch batch.json --baseline baseline.json
```

`batch.json` — a list of records `{"text": "...", "origin": "..."}`
`baseline.json` — a list of verified human-origin records `{"text": "..."}`

Origin labels: `verified_human`, `direct_synthetic`, `unknown_origin`,
`mixed_origin`, `recursive_synthetic`.

---

## What SDIR reports

A single score in `[0, 1]` plus the component signals that produced it:

| signal | what it catches |
|---|---|
| distribution shift | batch drifting away from the baseline |
| lineage concentration | sources collapsing toward one origin (counts as risk only when provenance is untrusted) |
| recursion drift | template repetition + loss of rare vocabulary, *relative to baseline* |
| diversity drift | corpus collapsing toward a single mode, *relative to baseline* |
| provenance uncertainty | share of the batch that is unverified/unknown (raises risk) |

Prototype triggers (first-generation, calibratable):

| SDIR | status | action |
|---|---|---|
| `< 0.15` | CLEAR | no material drift under the declared baseline/provenance/config (not an authorization to train) |
| `0.15 – 0.35` | MONITOR | some drift; log lineage and review |
| `0.35 – 0.60` | REVIEW | marked drift; decide if it is domain narrowness or recursive synthesis |
| `> 0.60` | SEVERE-DRIFT | large departure consistent with recursive synthesis; investigate before use |

---

## Scope — what ships and what does not

This repository is the **read-out layer**. It computes *observable, verifiable*
statistics: anyone can inspect the code, reproduce every number, and check the
signals against their own data. That transparency is deliberate.

What is **not** in this repository is the judgement-generating layer — *why*
these particular signals, how they are weighted at the structural level, and how
the thresholds are derived. That layer belongs to the underlying framework and
is not required to use, verify, or benefit from the read-out. The tool stands on
its own; the foundation stays with its author.

This is by design, not obfuscation: there is no hidden or irreversible code
here. What you run is exactly what you read.

---

## Citation

If you use SDIR, please cite:

> Hu-Yang, Qingyun (胡杨庆云). *HAS-Core :: SDIR — Synthetic Data Inbreeding Rate:
> A Formative-Layer Read-out for AI Training Data.* Harmondeg Institute for
> Philosophy & Practice, Calgary, Canada.
> DOI: [10.5281/zenodo.21778972](https://doi.org/10.5281/zenodo.21778972)
> ORCID: [0009-0006-3446-8439](https://orcid.org/0009-0006-3446-8439)

---

## Author

**Qingyun Hu-Yang (胡杨庆云)**
Harmondeg Institute for Philosophy & Practice, Calgary, Canada
Contact: contact@harmondeg.org

DOI: [10.5281/zenodo.21778972](https://doi.org/10.5281/zenodo.21778972)
ORCID: [0009-0006-3446-8439](https://orcid.org/0009-0006-3446-8439)

Part of the HAS formative-layer auditing programme. SDIR is the first of three
read-out protocols; PAC (representation anchoring) and CPC (causal-path
coherence) follow.

## License

**Non-Commercial Research License** — see [`LICENSE`](LICENSE).

Free for academic research, personal study, and non-commercial AI-safety
work, with attribution. **Commercial use of any kind is prohibited without
prior written permission from the author**, including modified, partial, or
reimplemented use. To license SDIR commercially, contact the author to
negotiate terms.
