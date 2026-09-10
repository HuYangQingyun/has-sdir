"""
HAS-Core :: SDIR detection core

The detection core is NOT included in this public demonstration build.

This file is a sealed placeholder. It exposes the core's interface so the
demonstration and tests run end to end, but it contains no detection method. The
working method lives in the engineering edition (internally at 3.0), which
reaches materially higher performance on real-world data and is provided only
through collaboration or commercial licensing.

    read_out(labels) -> (separated: bool, minority_fraction: float)

In this public build the read-out is driven by the provenance labels the caller
already supplies with the batch — it does not infer contamination itself. This
is deliberate: the public build demonstrates the effect and the reporting; it is
not the detector. To evaluate your own data with the real core, contact the
Harmondeg Institute (see the README).
"""
from __future__ import annotations

# provenance labels that count as synthetic contamination for the demonstration
_SYNTHETIC = {"direct_synthetic", "recursive_synthetic"}


def read_out(labels):
    """Public-build read-out.

    Reports separation and the contaminated fraction directly from the provenance
    labels supplied with the batch. It performs no detection of its own — the
    detector is not part of this build. Given honest labels it demonstrates the
    end-to-end reporting; it does not, and does not claim to, discover
    contamination on unlabeled data.
    """
    if not labels:
        return False, 0.0
    n = len(labels)
    synth = sum(1 for x in labels if x in _SYNTHETIC)
    frac = synth / n if n else 0.0
    minority = min(frac, 1.0 - frac)
    separated = 0.0 < frac < 1.0
    return separated, float(minority)
