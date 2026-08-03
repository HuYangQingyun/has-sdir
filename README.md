# HAS-Core :: SDIR

**Synthetic Data Inbreeding Rate** — a formative-layer read-out for AI training data.

> **License: Non-Commercial Research only.** Free for research and study.
> Commercial use requires prior written permission — see [LICENSE](LICENSE).

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

`demo.py` builds two contrasting corpora (no downloads), runs the read-out on
both, and writes `sdir_demo.png`. A healthy multi-source batch scores near zero;
a recursively-synthesised, source-collapsed batch trips the SEVERE trigger.

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
| distribution shift | batch drifting away from the human baseline |
| lineage concentration | sources collapsing toward one origin |
| recursion fingerprint | template repetition + loss of rare vocabulary |
| diversity contraction | the corpus collapsing toward a single mode |

Prototype triggers (first-generation, calibratable):

| SDIR | status | action |
|---|---|---|
| `< 0.08` | CLEAR | allow into training |
| `0.08 – 0.15` | MONITOR | increase source sampling |
| `0.15 – 0.30` | TRIGGER | quarantine high-risk subset |
| `> 0.30` | SEVERE | block batch; audit human data |

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
