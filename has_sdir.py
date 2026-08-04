"""
HAS-Core :: SDIR — Synthetic Data Inbreeding Rate
Formative Layer Auditing, Protocol III (public read-out module)

Author : Qingyun Hu-Yang (胡杨庆云)
Institute: Harmondeg Institute for Philosophy & Practice, Calgary, Canada
DOI     : 10.5281/zenodo.21778972
Contact : contact@harmondeg.org
License : Non-Commercial Research License — see LICENSE
Version : 1.1

------------------------------------------------------------------------
SCOPE AND STATUS  (read this first)
------------------------------------------------------------------------
SDIR is a compact, first-generation PROTOTYPE: a read-only proof-of-concept
for formative-layer auditing. It measures how far a batch has structurally
DRIFTED FROM A HUMAN BASELINE you supply, and how much its internal structure
shows the signatures of recursive synthesis. It is NOT a production system,
NOT intended to run at full training scale, and its score MUST NOT be used as
a standalone gate on a training decision. It is an instrument for
investigation, not authorization. A diagnosis is evidence; a separate policy
layer, not this score, decides whether an operation is permitted.

IMPORTANT — SDIR reports DRIFT FROM YOUR BASELINE, not a verdict of
"good vs bad" data. A batch can drift because it is recursively synthesised,
OR because it is legitimately narrow human text (one domain, one language,
one register). SDIR cannot, by itself, tell these apart. That judgement
belongs to whoever knows the data. To make the read-out meaningful, the
baseline MUST be matched to the batch's intended domain and language; a
mismatched baseline will report drift that is real but not a defect.

------------------------------------------------------------------------
WHAT THIS MODULE COMPUTES
------------------------------------------------------------------------
Given a batch (each record tagged with an origin label) and a human baseline,
it reports a score in [0,1] with the component signals that produced it:

    - distribution shift of the batch away from the baseline
    - source-lineage concentration (normalised Herfindahl index)
    - recursion fingerprint, measured RELATIVE TO the baseline
    - diversity contraction, measured RELATIVE TO the baseline

A HIGH score means the batch's structure departs markedly from the baseline
in ways consistent with recursive synthesis. Whether that departure is a
problem is a judgement for the data owner, informed by domain and baseline.

------------------------------------------------------------------------
v1.1 — HARDENING (in response to public adversarial review + self-audit)
------------------------------------------------------------------------
1. Fusion no longer lets one low signal cancel independent strong evidence
   (the v1.0 product form allowed a false CLEAR by relabelling provenance or
   contaminating the baseline).
2. Recursion and diversity are measured RELATIVE TO the baseline, so
   legitimately homogeneous human text no longer reads as recursive collapse
   purely because its internal similarity is high in absolute terms.
3. Provenance is treated conservatively: missing/undocumented origins become
   unknown_origin and RAISE uncertainty; they never become favourable.
4. Verdict language is drift-based ("departs from baseline"), not a
   good/bad ruling; CLEAR is narrowed accordingly.

The judgement-generating layer (why these signals, structural weighting,
threshold derivation) is NOT in this file and does not ship.
------------------------------------------------------------------------
"""

from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---- thresholds (drift from baseline; first-generation, calibratable) ----
SDIR_MONITOR = 0.15
SDIR_TRIGGER = 0.35
SDIR_SEVERE  = 0.60

VERIFIED_HUMAN   = "verified_human"
DIRECT_SYNTHETIC = "direct_synthetic"
UNKNOWN_ORIGIN   = "unknown_origin"
MIXED_ORIGIN     = "mixed_origin"
RECURSIVE_SYNTH  = "recursive_synthetic"
_KNOWN_ORIGINS = {VERIFIED_HUMAN, DIRECT_SYNTHETIC, UNKNOWN_ORIGIN,
                  MIXED_ORIGIN, RECURSIVE_SYNTH}
_TRUSTED = {VERIFIED_HUMAN}


@dataclass
class SDIRResult:
    sdir: float
    dist_shift: float
    lineage_concentration: float
    recursion_drift: float
    diversity_drift: float
    provenance_uncertainty: float
    origin_distribution: dict = field(default_factory=dict)
    trigger_status: str = ""
    recommended_action: str = ""
    notes: list = field(default_factory=list)

    def as_report(self) -> str:
        lines = [
            "HAS-Core :: SDIR Formative-Layer Read-out  (v1.1 prototype)",
            "reports DRIFT FROM BASELINE, not a good/bad verdict",
            "-" * 52,
            f"SDIR score ............... {self.sdir:.3f}",
            f"  distribution shift ..... {self.dist_shift:.3f}",
            f"  lineage concentration .. {self.lineage_concentration:.3f}",
            f"  recursion drift ........ {self.recursion_drift:.3f}",
            f"  diversity drift ........ {self.diversity_drift:.3f}",
            f"  provenance uncertainty . {self.provenance_uncertainty:.3f}",
            "-" * 52,
            f"Status ................... {self.trigger_status}",
            f"Recommended action ....... {self.recommended_action}",
            "-" * 52,
            "Origin distribution:",
        ]
        for k, v in self.origin_distribution.items():
            lines.append(f"  {k:<20} {v:>6.1%}")
        if self.notes:
            lines.append("-" * 52)
            lines.append("Notes:")
            for n in self.notes:
                lines.append(f"  - {n}")
        return "\n".join(lines)


def _normalise_origins(origins):
    clean, notes = [], []
    n_missing = n_invalid = 0
    for o in origins:
        if o is None or (isinstance(o, str) and o.strip() == ""):
            clean.append(UNKNOWN_ORIGIN); n_missing += 1
        elif o not in _KNOWN_ORIGINS:
            clean.append(UNKNOWN_ORIGIN); n_invalid += 1
        else:
            clean.append(o)
    if n_missing:
        notes.append(f"{n_missing} record(s) had no origin; treated as unknown_origin.")
    if n_invalid:
        notes.append(f"{n_invalid} record(s) had an undocumented origin label; "
                     f"treated as unknown_origin.")
    return clean, notes


def _provenance_uncertainty(origins):
    if not origins:
        return 1.0
    untrusted = sum(1 for o in origins if o not in _TRUSTED)
    return float(untrusted / len(origins))


def _distribution_shift(batch_vecs, base_vecs):
    b = batch_vecs.mean(axis=0); q = base_vecs.mean(axis=0)
    cos = float(cosine_similarity(b.reshape(1, -1), q.reshape(1, -1))[0, 0])
    return float(np.clip(1.0 - cos, 0.0, 1.0))


def _lineage_concentration(origins):
    counts = Counter(origins); m = len(counts)
    if m <= 1:
        return 1.0
    total = sum(counts.values())
    shares = np.array([c / total for c in counts.values()])
    hhi = float(np.sum(shares ** 2))
    return float((hhi - 1.0 / m) / (1.0 - 1.0 / m))


def _recursion_raw(texts):
    """Absolute recursion signature: opener repetition + hapax collapse."""
    if len(texts) < 2:
        return 0.0
    openers = [" ".join(re.findall(r"\w+", t.lower())[:4]) for t in texts]
    top_share = max(Counter(openers).values()) / len(texts)
    all_tokens = []
    for t in texts:
        all_tokens.extend(re.findall(r"\w+", t.lower()))
    if not all_tokens:
        return 0.0
    vocab = Counter(all_tokens)
    hapax_ratio = sum(1 for w, c in vocab.items() if c == 1) / len(vocab)
    tail_collapse = float(np.clip(1.0 - hapax_ratio / 0.5, 0.0, 1.0))
    return float(np.clip(0.5 * top_share + 0.5 * tail_collapse, 0.0, 1.0))


def _diversity_raw(vecs):
    if vecs.shape[0] < 2:
        return 0.0
    n = min(vecs.shape[0], 400)
    idx = np.random.default_rng(0).choice(vecs.shape[0], n, replace=False)
    sims = cosine_similarity(vecs[idx])
    return float(np.clip(float(np.mean(sims[np.triu_indices(n, k=1)])), 0.0, 1.0))


def _drift(batch_val, base_val):
    """How much a signal has moved ABOVE the baseline, normalised.
    Only upward movement (more recursive / more contracted) counts."""
    excess = max(0.0, batch_val - base_val)
    headroom = max(1e-6, 1.0 - base_val)
    return float(np.clip(excess / headroom, 0.0, 1.0))


def _soft_floor(x, floor):
    """Subtract a tolerance floor and renormalise. Values at or below the
    floor (normal sampling noise between same-distribution corpora) map to 0;
    only movement clearly above the floor counts as signal."""
    return float(np.clip((x - floor) / max(1e-6, 1.0 - floor), 0.0, 1.0))


def _fuse(dist_shift, lineage, recursion_drift, diversity_drift, prov_uncert,
          dist_floor=0.0):
    """v1.1 fusion. Text-intrinsic DRIFT (recursion, diversity relative to
    baseline) forms the evidence floor and cannot be vetoed by a single low
    signal. Distribution shift and lineage corroborate but cannot cancel it.
    Provenance uncertainty only adds risk.

    dist_floor is the baseline's own within-distribution sampling noise;
    distribution shift at or below it is not treated as drift, so a batch
    drawn from the same distribution as the baseline does not self-flag."""
    ds = _soft_floor(dist_shift, dist_floor)
    text_evidence = max(recursion_drift, diversity_drift) * 0.6 + \
                    (recursion_drift * diversity_drift) ** 0.5 * 0.4
    # Source concentration is only a RISK when provenance is untrusted.
    # A batch that is entirely verified_human is concentrated but not suspect,
    # so lineage contributes to risk in proportion to provenance uncertainty.
    lineage_risk = lineage * prov_uncert
    corrob = 1.0 - (1.0 - ds) * (1.0 - lineage_risk)        # noisy-OR
    lifted = text_evidence + (1.0 - text_evidence) * corrob * 0.35
    with_prov = lifted + (1.0 - lifted) * prov_uncert * 0.15
    return float(np.clip(with_prov, 0.0, 1.0))


def _status(sdir):
    if sdir < SDIR_MONITOR:
        return ("CLEAR",
                "Batch does not depart materially from the declared baseline "
                "under this provenance, code and configuration. Not an "
                "authorization to train.")
    if sdir < SDIR_TRIGGER:
        return ("MONITOR",
                "Some drift from baseline; log lineage and review whether it "
                "reflects domain or degradation.")
    if sdir < SDIR_SEVERE:
        return ("REVIEW",
                "Marked drift from baseline. Determine whether it is "
                "legitimate domain narrowness or recursive synthesis before "
                "using the batch.")
    return ("SEVERE-DRIFT",
            "Large structural departure from baseline consistent with "
            "recursive synthesis. Investigate before use; do not treat as "
            "training-ready on this signal alone.")


def compute_sdir(batch_texts, batch_origins, baseline_texts):
    """Run one SDIR read-out (v1.1 prototype).
    Reports drift of the batch from baseline. Baseline should match the
    batch's intended domain/language, or drift will be real but not a defect.
    """
    if len(batch_texts) != len(batch_origins):
        raise ValueError("batch_texts and batch_origins must align 1:1")
    if len(batch_texts) < 2 or len(baseline_texts) < 2:
        raise ValueError("need at least 2 documents in batch and baseline")

    origins, notes = _normalise_origins(batch_origins)

    vec = TfidfVectorizer(max_features=4096, stop_words="english")
    vec.fit(baseline_texts + batch_texts)
    batch_vecs = vec.transform(batch_texts).toarray()
    base_vecs  = vec.transform(baseline_texts).toarray()

    dist_shift = _distribution_shift(batch_vecs, base_vecs)
    lineage    = _lineage_concentration(origins)
    prov_uncert = _provenance_uncertainty(origins)

    # baseline self-noise: split the baseline in half and measure the shift
    # between the halves. Two same-distribution corpora still differ a little;
    # that amount is not drift, so it becomes the tolerance floor.
    if base_vecs.shape[0] >= 4:
        half = base_vecs.shape[0] // 2
        perm = np.random.default_rng(0).permutation(base_vecs.shape[0])
        b1 = base_vecs[perm[:half]]; b2 = base_vecs[perm[half:2*half]]
        dist_floor = _distribution_shift(b1, b2)
    else:
        dist_floor = 0.0

    # recursion & diversity measured RELATIVE TO baseline
    rec_batch = _recursion_raw(batch_texts)
    rec_base  = _recursion_raw(baseline_texts)
    div_batch = _diversity_raw(batch_vecs)
    div_base  = _diversity_raw(base_vecs)
    recursion_drift = _drift(rec_batch, rec_base)
    diversity_drift = _drift(div_batch, div_base)

    sdir = _fuse(dist_shift, lineage, recursion_drift, diversity_drift,
                 prov_uncert, dist_floor=dist_floor)
    status, action = _status(sdir)

    if prov_uncert >= 0.5:
        notes.append(f"{prov_uncert:.0%} of the batch is unverified/unknown "
                     f"provenance; provenance evidence is weak (raises uncertainty).")
    notes.append("SDIR reports drift from the supplied baseline, not a good/bad "
                 "verdict. Ensure the baseline matches the batch's domain.")

    total = len(origins)
    dist = {k: v / total for k, v in Counter(origins).items()}

    return SDIRResult(
        sdir=sdir, dist_shift=dist_shift, lineage_concentration=lineage,
        recursion_drift=recursion_drift, diversity_drift=diversity_drift,
        provenance_uncertainty=prov_uncert, origin_distribution=dist,
        trigger_status=status, recommended_action=action, notes=notes,
    )
