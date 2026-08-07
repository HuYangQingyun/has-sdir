# SDIR — Changelog & Progress Record

## v2.0 (current)

**The change:** from a pooled-average view to a **distribution region-separation**
view. v1.1 pooled signals across a batch and compared to a baseline, which
averaged a synthetic minority against a human majority and lost partial
contamination. v2.0 looks at whether the batch's distribution has separated into
two regions (a foreign population mixed into a native one), which lets partial
contamination surface and be quantified.

**Added:**
- Multilingual support: English, Chinese (jieba), French, Spanish, German, with
  automatic language detection.
- Engineering hardening: small samples return `insufficient`/`UNOBSERVED`;
  unknown provenance is its own state and does not raise the score; baseline
  lock uses stable SHA-256 + operator-supplied secret.

**Verified in internal testing:** clean batch reads clear (no false alarm);
~30–50% synthetic flagged and quantified; cosmetic evasion caught; narrow human
text not condemned; deterministic; multilingual detection on en/zh/fr/es/de.

**Honest boundaries (documented in README):** light contamination (<20%) less
stable; a mid-range blind spot near 25% (inherent to a low-dimensional view);
highly human-like / impoverished synthetic inseparable by any lightweight
method; multilingual false positives on very limited vocabulary; whole-batch
(near-100%) synthetic out of scope (batch-contamination detector, not a
single-document classifier); baseline does not participate in scoring
(BaselineLock is a tamper-lock only).

**Stress-tested by:** independent adversarial review, plus cross-checks from
multiple external AI systems. Findings were either fixed (hardening above) or
documented honestly as inherent boundaries of a lightweight statistical method.

## Next: Engineering Edition (commercial / collaborative)

Stable detection across the full contamination range, multi-dimensional
observation that removes the mid-range blind spot, resilience to highly
human-like synthetic text, and scaling to large, high-throughput settings.

## v1.1 (previous)

Pooled-average drift measure against a baseline. Superseded by v2.0 after review
showed pooling lost partial contamination.
