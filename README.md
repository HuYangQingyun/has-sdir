# HAS-Core :: SDIR v2.0

**Synthetic Data Inbreeding Rate** — a read-only, formative-layer read-out for
the integrity of training data. It examines a batch *before* a model trains on
it, and reports how far the batch has separated from a human reference in ways
consistent with synthetic recursion.

License: Non-Commercial Research only. Free for research and study. Commercial
use requires prior written permission — see LICENSE.

---

> **Scope & status (read first).** SDIR is a **lightweight, minimal
> demonstration**. Its purpose is to show a *direction*: that the integrity of
> training data can be examined at the **formative layer**, before a model
> trains on it, and to make that examination runnable so its value can be seen.
> It is **not** a production detector and does **not** claim to solve synthetic
> data detection outright. It is **read-only**: it reports evidence, it does not
> decide. A diagnosis is evidence; a separate policy layer decides.
>
> The objective of this public build is not to replace engineering validation,
> but to provide a lightweight **structural observation layer** that complements
> existing evaluation pipelines. It sits upstream of the usual checks and looks
> at the shape of a batch, alongside — not instead of — the work that groups
> like METR, Apollo, and the national labs already do.
>
> A robust, engineering-grade implementation — stable across the full range of
> contamination, resilient to highly human-like synthetic text, and able to
> scale — is a heavier undertaking, referred to below as the **Engineering
> Edition** (commercial / collaborative).

---

## What changed from v1.1

v1.1 measured drift by **pooling** signals across the whole batch and comparing
the pooled figure to a baseline. Independent adversarial review showed the
pooling averaged a synthetic minority against a human majority, so **partial
contamination — the realistic case — was lost before any comparison happened.**

v2.0 changes the frame. It no longer asks whether a pooled average crosses a
line. It looks at the **distribution** of the batch and whether that
distribution has **separated into two regions** — the signature of a foreign
population mixed into a native one. This is a distribution view rather than an
average view, and it is what allows partial contamination to surface at all.

This direction came out of an exchange with an independent reviewer, whose point
that the problem was in the pooling and not in a threshold sent the work down a
more productive path. With thanks for that.

v2.0 also extends beyond English to **Chinese, French, Spanish and German**,
with automatic language detection.

---

## What it does well

On realistic corpora — a genuinely varied human reference against actual
synthetic text — the distribution view **detects and quantifies mid-range
contamination** and does **not** raise a false alarm on clean human data. In
internal testing:

- A **clean human batch** reads clear (no false alarm).
- A batch **~30–50% synthetic** is flagged, and the estimated contaminated
  fraction tracks the true proportion.
- **Cosmetic evasion** (rotated openers, injected rare tokens) is markedly less
  effective against a distribution view than against the pooled signals of v1.1,
  because it changes surface numbers, not the fact that a foreign population
  still forms its own region.
- **Narrow but genuine human text** is not condemned as synthetic.
- Behaviour is **deterministic**: the same input gives the same read-out.
- Provenance uncertainty and small-sample status are reported as **their own
  states**, not folded into the score (see below).

---

## Known boundaries (found in our own testing)

These are stated plainly. They are not hidden, and they are, in good part,
**limits shared by any lightweight statistical approach** — not peculiar to this
one. Where a boundary is reached, that is the work the Engineering Edition, or a
direct collaboration, is for.

- **Light contamination (roughly under 20%).** When the synthetic share is
  small, the two populations have not yet separated cleanly, and detection
  becomes **less stable**.

- **A mid-range blind spot (around 25%).** At certain mid-range levels — in our
  testing, near 25% — the two populations can **overlap on the single
  statistical dimension** this lightweight build observes, and detection can
  miss even though 20% and 30% are caught. This is an **inherent property of a
  low-dimensional statistical view, not an implementation bug**: when two
  populations coincide on the one dimension being measured, no single-dimension
  test separates them. A multi-dimensional implementation — observing several
  interacting signals rather than one position — resolves it, and is part of the
  Engineering Edition.

- **Synthetic text that is highly similar to human text.** If synthetic and
  human writing are statistically close — for instance in a deliberately
  impoverished test corpus where both are reduced to the same small, templated
  vocabulary — **no lightweight statistical method can separate them, including
  this one.** This is the data being genuinely inseparable, not a fault in the
  method. On richer, real-world corpora the two are further apart and detection
  is more reliable.

- **Multilingual on impoverished vocabulary.** The multilingual path can raise
  **false positives when the vocabulary is very limited** (short, highly
  templated text), for the same reason: with little lexical variety, normal and
  foreign populations look alike. It is more reliable on natural, varied text.

- **Whole-batch synthetic (near 100%).** Region-separation detects a *minority*
  mixed into a majority; when the batch is entirely synthetic there is no second
  region to find. Note this is a **difference of job, not a weakness**: SDIR is a
  *batch-contamination* detector (how much foreign material is mixed in), not a
  *single-document* AI-text classifier (is this one document AI-written). Tools
  like DetectGPT or GPTZero do the latter; that is a different task.

- **The baseline does not participate in scoring.** In v2.0 the read-out is
  **intrinsic to the batch** — the distribution view looks at the batch's own
  separation, so the score does not depend on the supplied baseline. The
  `BaselineLock` provided is therefore a **tamper-lock** (so a reference cannot
  be silently swapped in a pipeline that does use one), **not** a component of
  the score. This also means v2.0 is largely immune to baseline poisoning by
  construction.

**Why this matters, stated honestly:** we would rather name these boundaries
than have someone meet them unawares. Knowing where the light version reaches
its limit is exactly what lets the Engineering Edition be built with confidence
for the case in hand.

---

## Engineering hardening in this build

Beyond the core method, v2.0 makes the read-out honest under edge conditions:

- **Small samples** (fewer than ten documents) return an **`insufficient` /
  `UNOBSERVED`** status — "cannot observe" is never reported as "nothing wrong".
- **Unknown provenance** is reported as its own state and does **not** by itself
  raise the contamination score (unknown is not treated as dangerous).
- **The baseline lock** uses a stable SHA-256 fingerprint and an
  operator-supplied secret (not a hardcoded token); with no secret configured it
  is immutable.

---

## What the Engineering Edition adds (collaboration / commercial)

The boundaries above are addressed by an engineering-grade build: stable
detection across the full contamination range, resilience to highly human-like
synthetic text, multi-dimensional observation that removes the mid-range blind
spot, and scaling to large, high-throughput settings. This is offered through
direct collaboration and commercial licensing.

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

Contact: contact@harmondeg.org
