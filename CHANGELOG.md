# SDIR — Changelog

## v2.0 (current)

**The change:** from a pooled-average view to a **distribution region-separation**
view. v1.1 pooled signals across a batch and compared to a baseline, which
averaged a synthetic minority against a human majority and lost partial
contamination. v2.0 looks at whether the batch's distribution has separated into
two regions (a foreign population mixed into a native one), which lets partial
contamination surface and be quantified.

**Added:**
- Multilingual support: English, Chinese, French, Spanish, German, with
  automatic language detection.
- Engineering hardening: small samples return `insufficient`/`UNOBSERVED`;
  unknown provenance is its own state and does not raise the score; baseline
  lock uses a stable SHA-256 fingerprint + operator-supplied secret.

**Behaviour:** a clean batch reads clear (no false alarm); contaminated batches
are flagged and quantified; the read-out is deterministic and reports its own
observation state honestly (it never reports "cannot observe" as "clean").

**Scope:** this is a lightweight, public demonstration build. It is a
batch-contamination diagnostic, not a single-document classifier. As with any
lightweight statistical method, there are conditions under which separation is
inherently hard; these are the cases a full engineering implementation is built
for. This build is read-only: it reports evidence, it does not decide.

## Next

A robust, engineering-grade edition — stronger, more resilient, and able to
scale — is offered through collaboration and commercial licensing.

## v1.1 (previous)

Pooled-average drift measure against a baseline. Superseded by v2.0.
