# SDIR — Changelog

## Public demonstration build (current)

- Multilingual read-out: English, Chinese, French, Spanish, German, with
  automatic language detection.
- Honest edge-case behaviour: small samples return `insufficient` / `UNOBSERVED`
  (never reported as clean); unknown provenance is its own state and does not
  raise the score; the read-out is deterministic.
- Baseline lock: a reference set cannot be silently swapped or loosened without
  an operator-supplied secret.

This build is read-only and reports evidence; it does not decide. It is a
demonstration of the effect. The detection core is not part of the public build.

## Engineering edition (3.0) — not published

An engineering-grade edition reaches materially higher performance on real-world
data. It is not published, and is provided only through collaboration or
commercial licensing. See the README.
