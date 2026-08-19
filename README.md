# HAS-Core :: SDIR v2.0

**SDIR — Synthetic Data Inbreeding Rate.** A read-only, formative-layer
diagnostic for the integrity of training data. It examines a batch *before* a
model trains on it, and reports the degree to which the batch shows signs of
synthetic-data contamination consistent with recursive ("inbreeding") reuse.

**License:** Non-Commercial Research only. Free for research and study.
Commercial use requires prior written permission — see `LICENSE`.

---

## Scope & status (please read first)

SDIR is a **lightweight, public demonstration build**. Its purpose is to make a
direction visible and runnable: that the integrity of training data can be
examined at the **formative layer**, before a model trains on it.

- It is **read-only** — it reports evidence, it does not decide. A diagnosis is
  evidence; a separate policy layer decides.
- It is a **demonstration**, not a production detector. The core of the method
  in this public build is intentionally minimal — enough to show the effect,
  not the full implementation.
- A robust, engineering-grade implementation for a specific setting is a
  separate undertaking, referred to below as the **Engineering Edition**,
  offered through collaboration or commercial licensing.

---

## The problem it addresses

Modern AI training increasingly reuses AI-generated data. Training successive
models on synthetic data drives recursive degradation — the output distribution
narrows and diversity collapses ("model collapse"). Once training data is
contaminated at the source, everything downstream — evaluation, alignment,
deployment — is built on a compromised foundation.

SDIR sits at this upstream point: a provenance-integrity read-out on the data
**before** it ever enters training. It complements existing model-evaluation
work and sits upstream of it — alongside, not instead of, that work.

---

## What it reports

Given a batch of documents, SDIR returns:

- a **contamination read-out** (an SDIR score),
- a **graded status** — `CLEAR` / `MONITOR` / `REVIEW` / `SEVERE-DRIFT`,
- and separate **observation states** for cases where a clean reading cannot be
  given (see "Honest behaviour" below).

It is **multilingual**, with automatic language detection across English,
Chinese, French, Spanish and German.

---

## What it is, and is not

SDIR is a **batch-contamination** diagnostic: it reports *how far a batch shows
signs of synthetic contamination as a whole*. It is **not** a single-document
AI-text classifier — it does not claim to decide whether one specific document
was AI-written. Tools such as DetectGPT or GPTZero address that different task.

As a lightweight statistical read-out, SDIR is deliberately **general, not
domain-specific**. Highly formulaic or narrowly templated text — in any single
domain — can sit close to the line for lightweight methods generally. Where a
particular domain matters, the right answer is a **calibrated layer built for
that domain**, added on request — not the general tool stretched to fit.

---

## Honest behaviour under edge conditions

The read-out is built not to overclaim:

- **Small samples** return an `insufficient` / `UNOBSERVED` status — "cannot
  observe" is never reported as "nothing wrong".
- **Unknown provenance** is reported as its own state and does not by itself
  raise the contamination score — unknown is not treated as dangerous.
- Behaviour is **deterministic** — the same input gives the same read-out.
- A **BaselineLock** is provided as a tamper-lock: where a reference set is used
  in a pipeline, it cannot be silently swapped or loosened without an
  operator-supplied secret.

---

## The Engineering Edition (collaboration / commercial)

This public build shows the direction. A robust, engineering-grade
implementation — stable across a wider range of conditions, resilient to
harder cases, and able to scale to large, high-throughput settings — is a
heavier undertaking. It is offered through **direct collaboration and
commercial licensing**.

**We are actively seeking capable, well-resourced partners** — institutions and
individuals with the strength, the resources, and a track record to build at
scale — to take this further: to test and validate, to build the Engineering
Edition together, and to pursue joint reporting and enterprise development.
This is an open invitation, and we welcome conversations to explore it.

---

## Files

- `has_sdir.py` — the v2.0 read-out (public demonstration build)
- `multilang.py` — multilingual tokenization (en, zh, fr, es, de)
- `demo.py` — runnable demonstration
- `LICENSE` — non-commercial research license

## Use

```python
from has_sdir import compute_sdir, VERIFIED_HUMAN

result = compute_sdir(batch_texts, batch_origins, baseline_texts)
print(result.as_report())
```

---

**Harmondeg Institute for Philosophy & Practice (HIPP)**
Qingyun Hu-Yang · Calgary, Alberta, Canada
Tel: +1 403 702 6608
Email: contact@harmondeg.org / huqingyun@hotmail.com
GitHub: https://github.com/HuYangQingyun/has-sdir
