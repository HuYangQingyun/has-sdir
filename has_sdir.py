"""
HAS-Core :: SDIR — Synthetic Data Inbreeding Rate
Formative Layer Auditing, Protocol III (public read-out module)

Author : Qingyun Hu-Yang (胡杨庆云)
Institute: Harmondeg Institute for Philosophy & Practice, Calgary, Canada
DOI     : 10.5281/zenodo.21778972
Contact : contact@harmondeg.org
License : Non-Commercial Research License — see LICENSE

------------------------------------------------------------------------
WHAT THIS MODULE IS
------------------------------------------------------------------------
This is the *read-out* layer of the SDIR protocol. Given a batch of text
records (each tagged with an origin label) and a verified human-origin
baseline, it reports a single normalised score in [0, 1] together with the
component signals that produced it:

    - distribution shift of the batch away from the human baseline
    - source-lineage concentration (normalised Herfindahl index)
    - recursive-synthesis fingerprint (template / low-frequency collapse)
    - semantic diversity contraction

A HIGH SDIR means the batch shows source contraction, recursive synthesis
and diversity loss — i.e. the data is beginning to feed on itself.

------------------------------------------------------------------------
WHAT THIS MODULE IS NOT
------------------------------------------------------------------------
The *why* — why these particular signals, how the fusion is weighted at the
structural level, and how the trigger thresholds are derived from the
underlying Harmondeg stability judgement — is NOT contained here. This file
computes observable statistics anyone can verify. It does not contain, and
cannot be reverse-engineered into, the judgement-generating layer. The core
never ships.
------------------------------------------------------------------------
"""

from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ----------------------------------------------------------------------
# Prototype thresholds (first-generation, calibratable)
# ----------------------------------------------------------------------
SDIR_MONITOR = 0.08   # below: clean; above: begin monitoring
SDIR_TRIGGER = 0.15   # above: significant recursive-synthesis risk
SDIR_SEVERE  = 0.30   # above: severe source contraction


# ----------------------------------------------------------------------
# Origin labels
# ----------------------------------------------------------------------
VERIFIED_HUMAN   = "verified_human"
DIRECT_SYNTHETIC = "direct_synthetic"
UNKNOWN_ORIGIN   = "unknown_origin"
MIXED_ORIGIN     = "mixed_origin"
RECURSIVE_SYNTH  = "recursive_synthetic"


@dataclass
class SDIRResult:
    sdir: float
    dist_shift: float
    lineage_concentration: float
    recursion_fingerprint: float
    diversity_contraction: float
    origin_distribution: dict = field(default_factory=dict)
    trigger_status: str = ""
    recommended_action: str = ""

    def as_report(self) -> str:
        lines = [
            "HAS-Core :: SDIR Formative-Layer Read-out",
            "-" * 44,
            f"SDIR score ............... {self.sdir:.3f}",
            f"  distribution shift ..... {self.dist_shift:.3f}",
            f"  lineage concentration .. {self.lineage_concentration:.3f}",
            f"  recursion fingerprint .. {self.recursion_fingerprint:.3f}",
            f"  diversity contraction .. {self.diversity_contraction:.3f}",
            "-" * 44,
            f"Trigger status ........... {self.trigger_status}",
            f"Recommended action ....... {self.recommended_action}",
            "-" * 44,
            "Origin distribution:",
        ]
        for k, v in self.origin_distribution.items():
            lines.append(f"  {k:<20} {v:>6.1%}")
        return "\n".join(lines)


# ----------------------------------------------------------------------
# Component signals (all observable, all verifiable)
# ----------------------------------------------------------------------
def _distribution_shift(batch_vecs: np.ndarray, base_vecs: np.ndarray) -> float:
    """Normalised divergence between batch and human baseline in TF-IDF space.
    Uses mean-embedding cosine distance as a stable, dependency-light proxy."""
    b = batch_vecs.mean(axis=0)
    q = base_vecs.mean(axis=0)
    cos = float(cosine_similarity(b.reshape(1, -1), q.reshape(1, -1))[0, 0])
    return float(np.clip(1.0 - cos, 0.0, 1.0))


def _lineage_concentration(origins: list[str]) -> float:
    """Normalised Herfindahl index over origin labels.
    0 = perfectly diverse sources, 1 = single source."""
    counts = Counter(origins)
    m = len(counts)
    if m <= 1:
        return 1.0
    total = sum(counts.values())
    shares = np.array([c / total for c in counts.values()])
    hhi = float(np.sum(shares ** 2))
    return float((hhi - 1.0 / m) / (1.0 - 1.0 / m))


def _recursion_fingerprint(texts: list[str]) -> float:
    """Detects template repetition and low-frequency-expression collapse —
    signatures of text that has passed repeatedly through generative models."""
    if len(texts) < 2:
        return 0.0

    # (a) opening-template repetition: how often documents share their first
    #     few tokens — recursive synthetic text tends to converge on openers.
    openers = []
    for t in texts:
        toks = re.findall(r"\w+", t.lower())
        openers.append(" ".join(toks[:4]))
    opener_counts = Counter(openers)
    top_share = max(opener_counts.values()) / len(texts)

    # (b) low-frequency vocabulary collapse: healthy human corpora have a long
    #     tail of rare words; recursively synthesised corpora lose it.
    all_tokens = []
    for t in texts:
        all_tokens.extend(re.findall(r"\w+", t.lower()))
    if not all_tokens:
        return 0.0
    vocab = Counter(all_tokens)
    hapax = sum(1 for w, c in vocab.items() if c == 1)
    hapax_ratio = hapax / len(vocab)                  # high in healthy text
    tail_collapse = float(np.clip(1.0 - hapax_ratio / 0.5, 0.0, 1.0))

    return float(np.clip(0.5 * top_share + 0.5 * tail_collapse, 0.0, 1.0))


def _diversity_contraction(batch_vecs: np.ndarray) -> float:
    """Semantic-network contraction: mean pairwise similarity inside the batch.
    High internal similarity = the corpus is collapsing toward a single mode."""
    if batch_vecs.shape[0] < 2:
        return 0.0
    n = min(batch_vecs.shape[0], 400)                 # cap for cost
    idx = np.random.default_rng(0).choice(batch_vecs.shape[0], n, replace=False)
    sims = cosine_similarity(batch_vecs[idx])
    iu = np.triu_indices(n, k=1)
    mean_sim = float(np.mean(sims[iu]))
    return float(np.clip(mean_sim, 0.0, 1.0))


# ----------------------------------------------------------------------
# Fusion  (public form: transparent product-of-signals proxy)
# ----------------------------------------------------------------------
def _fuse(dist_shift, lineage, recursion, diversity, gamma: float = 2.2) -> float:
    """Public composite proxy. The signals are combined multiplicatively so
    that risk registers only when several independent indicators co-occur —
    a single elevated signal alone will not trip the score.

    NOTE: this transparent proxy is what ships. The structural weighting that
    ties these signals to the underlying stability judgement is not here."""
    eps = 1e-6
    raw = (dist_shift * lineage * recursion * (0.5 + diversity)) / (1.0 + eps)
    return float(1.0 - np.exp(-gamma * raw))


def _status(sdir: float) -> tuple[str, str]:
    if sdir < SDIR_MONITOR:
        return "CLEAR", "Allow batch into training."
    if sdir < SDIR_TRIGGER:
        return "MONITOR", "Increase source sampling; log lineage."
    if sdir < SDIR_SEVERE:
        return "TRIGGER", "Quarantine high-risk subset; add verified human data."
    return "SEVERE", "Block batch from training; full human data audit."


# ----------------------------------------------------------------------
# Public entry point
# ----------------------------------------------------------------------
def compute_sdir(
    batch_texts: list[str],
    batch_origins: list[str],
    baseline_texts: list[str],
) -> SDIRResult:
    """Run one SDIR read-out.

    batch_texts    : documents in the batch under audit
    batch_origins  : origin label per document (see label constants)
    baseline_texts : verified human-origin reference corpus
    """
    if len(batch_texts) != len(batch_origins):
        raise ValueError("batch_texts and batch_origins must align 1:1")
    if len(batch_texts) < 2 or len(baseline_texts) < 2:
        raise ValueError("need at least 2 documents in batch and baseline")

    vec = TfidfVectorizer(max_features=4096, stop_words="english")
    vec.fit(baseline_texts + batch_texts)
    batch_vecs = vec.transform(batch_texts).toarray()
    base_vecs  = vec.transform(baseline_texts).toarray()

    dist_shift = _distribution_shift(batch_vecs, base_vecs)
    lineage    = _lineage_concentration(batch_origins)
    recursion  = _recursion_fingerprint(batch_texts)
    diversity  = _diversity_contraction(batch_vecs)

    sdir = _fuse(dist_shift, lineage, recursion, diversity)
    status, action = _status(sdir)

    total = len(batch_origins)
    dist = {k: v / total for k, v in Counter(batch_origins).items()}

    return SDIRResult(
        sdir=sdir,
        dist_shift=dist_shift,
        lineage_concentration=lineage,
        recursion_fingerprint=recursion,
        diversity_contraction=diversity,
        origin_distribution=dist,
        trigger_status=status,
        recommended_action=action,
    )
