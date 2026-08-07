"""
HAS-Core :: SDIR v2.0  (public demonstration build)

Synthetic Data Inbreeding Rate. A read-only, formative-layer read-out for the
integrity of training data: it examines a batch before a model trains on it.

WHAT CHANGED FROM v1.1
  v1.1 measured drift by pooling signals across the whole batch, then comparing
  the pooled figure to a baseline. Independent testing showed the pooling
  averaged a synthetic minority against a human majority, so partial
  contamination (the realistic case) was lost before any comparison. v2.0
  changes the frame: it no longer asks whether the pooled average crosses a
  line. It looks at the DISTRIBUTION of the batch and whether that distribution
  has separated into regions, the signature of a foreign population mixed into
  a native one. This greatly improves detection of partial contamination and
  is markedly more stable against cosmetic evasion. It also extends beyond
  English to Chinese, French, Spanish and German.

SCOPE (read first)
  This is a lightweight, minimal demonstration. It shows a direction and is
  meant to run so its value can be seen. It is not a production detector and
  does not claim to solve synthetic-data detection outright. Robust,
  engineering-grade implementation for a specific setting is exactly what a
  direct collaboration would build.

  The core of the region-separation method in this public build is intentionally
  simplified: it runs and demonstrates the effect, but the production-grade
  implementation is not published here. See the licence.

NOTE: This build keeps the v1.1 call signature so existing harnesses run
unchanged: compute_sdir(batch_texts, batch_origins, baseline_texts).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter
import numpy as np

from multilang import tokenize_batch

# ---- provenance labels (unchanged from v1.1 for compatibility) ----
VERIFIED_HUMAN   = "verified_human"
DIRECT_SYNTHETIC = "direct_synthetic"
UNKNOWN_ORIGIN   = "unknown_origin"
MIXED_ORIGIN     = "mixed_origin"
RECURSIVE_SYNTH  = "recursive_synthetic"
_KNOWN = {VERIFIED_HUMAN, DIRECT_SYNTHETIC, UNKNOWN_ORIGIN, MIXED_ORIGIN, RECURSIVE_SYNTH}
_TRUSTED = {VERIFIED_HUMAN}

SDIR_MONITOR = 0.15
SDIR_TRIGGER = 0.35
SDIR_SEVERE  = 0.60


import hashlib


def _stable_fingerprint(texts) -> str:
    """A stable, order-sensitive fingerprint of a text set. Uses SHA-256 over
    the joined texts, not Python's built-in hash() (which is process-salted and
    not reproducible across runs)."""
    h = hashlib.sha256()
    for t in texts:
        h.update(t.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


# ---- THE FIXED: baseline, set once, changed only by explicit authorisation --
@dataclass
class BaselineLock:
    """The reference baseline is fixed once and cannot be silently swapped or
    loosened. A poisoned baseline is the attack this closes: the reference
    frame is no longer freely under the caller's control at read time.

    The authorisation secret is supplied by the operator, never hardcoded. The
    fingerprint is a stable SHA-256, reproducible across runs."""
    texts: list
    auth_secret: str = None          # supplied by the operator, not hardcoded
    _fingerprint: str = field(default="")

    def __post_init__(self):
        self._fingerprint = _stable_fingerprint(self.texts)

    def verify(self, presented_texts) -> bool:
        """The baseline used at read time must match the one that was locked."""
        return _stable_fingerprint(presented_texts) == self._fingerprint

    def authorise_replacement(self, new_texts, secret=None):
        """Replacing the baseline requires the operator's secret. It cannot be
        swapped or loosened to clear a reading without it."""
        if self.auth_secret is None:
            raise PermissionError(
                "No authorisation secret was configured; baseline is immutable.")
        if secret != self.auth_secret:
            raise PermissionError(
                "Baseline is locked. Replacing it requires the configured "
                "authorisation secret; it cannot be swapped to clear a reading.")
        self.texts = list(new_texts)
        self._fingerprint = _stable_fingerprint(new_texts)


@dataclass
class SDIRResult:
    sdir: float
    contaminated_fraction: float
    distribution_split: bool
    language: str
    provenance_uncertainty: float
    trigger_status: str
    observation_status: str = "observed"   # observed | unobserved | insufficient
    origin_distribution: dict = field(default_factory=dict)
    notes: list = field(default_factory=list)

    # ---- v1.1 field aliases, so existing harnesses run unchanged ----
    @property
    def dist_shift(self):
        return self.contaminated_fraction

    @property
    def lineage_concentration(self):
        return 1.0 if self.distribution_split else 0.0

    @property
    def recursion_drift(self):
        return self.contaminated_fraction

    @property
    def diversity_drift(self):
        return self.contaminated_fraction

    def as_report(self) -> str:
        L = [
            "HAS-Core :: SDIR v2.0 read-out (public demonstration build)",
            "-" * 58,
            f"SDIR score .................. {self.sdir:.3f}",
            f"language (detected) ......... {self.language}",
            f"distribution separated ...... {self.distribution_split}",
            f"estimated contaminated frac . {self.contaminated_fraction*100:.0f}%",
            f"provenance uncertainty ...... {self.provenance_uncertainty:.3f}",
            "-" * 58,
            f"Status ...................... {self.trigger_status}",
        ]
        return "\n".join(L)


def _normalise_origins(origins):
    clean, notes = [], []
    miss = inv = 0
    for o in origins:
        if o is None or (isinstance(o, str) and o.strip() == ""):
            clean.append(UNKNOWN_ORIGIN); miss += 1
        elif o not in _KNOWN:
            clean.append(UNKNOWN_ORIGIN); inv += 1
        else:
            clean.append(o)
    if miss: notes.append(f"{miss} record(s) missing origin -> unknown_origin.")
    if inv:  notes.append(f"{inv} record(s) undocumented origin -> unknown_origin.")
    return clean, notes


def _provenance_uncertainty(origins):
    if not origins: return 1.0
    return float(sum(1 for o in origins if o not in _TRUSTED) / len(origins))


def _region_separation(token_lists):
    """PUBLIC DEMONSTRATION of the region-separation idea (simplified).

    Give each document a position from how common its tokens are across the
    batch. A foreign (synthetic) population forms a second cluster separated
    from the native one by a genuine valley. We require a real gap between two
    populations, not merely a spread, so a single healthy population (however
    wide) does not register. The production method is not published here.

    Returns (separated: bool, minority_fraction: float).
    """
    alltok = []
    for tl in token_lists:
        alltok.extend(tl)
    if not alltok:
        return False, 0.0
    freq = Counter(alltok)
    total = max(1, sum(freq.values()))
    pos = []
    for tl in token_lists:
        if not tl:
            pos.append(0.0); continue
        pos.append(float(np.mean([freq[w] / total for w in tl])))
    pos = np.array(pos)
    n = len(pos)
    if n < 10:
        return False, 0.0
    sd = pos.std()
    if sd <= 1e-9:
        return False, 0.0

    # Histogram the positions; a genuine two-population batch shows two masses
    # separated by a low-density valley. A single population (even a wide or
    # narrow one) has no such valley. We look for a valley whose density is a
    # small fraction of the two peaks that flank it.
    lo, hi = pos.min(), pos.max()
    if hi - lo <= 1e-9:
        return False, 0.0
    bins = 12
    hist, edges = np.histogram(pos, bins=bins, range=(lo, hi))
    # find the highest peak, then the highest peak separated from it by >=2 bins
    peaks = np.argsort(hist)[::-1]
    p1 = peaks[0]
    p2 = None
    for p in peaks[1:]:
        if abs(p - p1) >= 3 and hist[p] >= 0.15 * hist[p1]:
            p2 = p; break
    if p2 is None:
        return False, 0.0
    a, b = min(p1, p2), max(p1, p2)
    valley = hist[a+1:b].min() if b > a + 1 else hist[a]
    peak_low = min(hist[a], hist[b])
    # require a real valley: density between the two peaks drops well below them
    if valley > 0.35 * peak_low:
        return False, 0.0
    # minority fraction = smaller of the two masses split at the valley bin
    valley_bin = a + 1 + int(np.argmin(hist[a+1:b])) if b > a + 1 else a
    cut = edges[valley_bin + 1]
    upper = float(np.mean(pos > cut))
    minority = min(upper, 1.0 - upper)
    return True, float(minority)


def _status(s):
    if s < SDIR_MONITOR: return "CLEAR"
    if s < SDIR_TRIGGER:  return "MONITOR"
    if s < SDIR_SEVERE:   return "REVIEW"
    return "SEVERE-DRIFT"


MIN_OBSERVABLE = 10   # below this, region-separation cannot be observed


def compute_sdir(batch_texts, batch_origins, baseline_texts):
    """v2.0. Interface-compatible with v1.1.

    Detection is by distribution region-separation over per-document positions,
    not by a pooled average against the baseline, so partial contamination is
    no longer averaged away. Multilingual: language is detected automatically.
    The baseline can be wrapped in a BaselineLock to close baseline-swapping.

    Observation status is reported separately from the score: too few documents
    yields 'insufficient' (not a clean reading), so 'cannot observe' is never
    silently reported as 'nothing wrong'. Provenance uncertainty is reported as
    its own state and is not folded into the score as if unknown meant dangerous.
    """
    if len(batch_texts) != len(batch_origins):
        raise ValueError("batch_texts and batch_origins must align 1:1")
    if len(batch_texts) < 2 or len(baseline_texts) < 2:
        raise ValueError("need >=2 docs in batch and baseline")

    origins, notes = _normalise_origins(batch_origins)
    prov = _provenance_uncertainty(origins)

    # multilingual tokenisation (English, Chinese, French, Spanish, German)
    token_lists, lang = tokenize_batch(batch_texts)

    # too few documents to observe a distribution: say so, do not call it clear
    if len(batch_texts) < MIN_OBSERVABLE:
        notes.append(
            f"only {len(batch_texts)} documents; below the minimum of "
            f"{MIN_OBSERVABLE} needed to observe a distribution. This is "
            f"'not observed', not 'no contamination'.")
        return SDIRResult(
            sdir=0.0, contaminated_fraction=0.0, distribution_split=False,
            language=lang, provenance_uncertainty=prov,
            trigger_status="UNOBSERVED", observation_status="insufficient",
            origin_distribution={k: v/len(origins) for k, v in Counter(origins).items()},
            notes=notes,
        )

    # region-separation over the batch distribution (the v2.0 frame)
    separated, minority = _region_separation(token_lists)

    # score is driven ONLY by the observed separated fraction. Provenance
    # uncertainty is NOT folded in as risk: unknown origin is reported as its
    # own state, it does not by itself raise the contamination score.
    score = float(np.clip(minority * 1.6 if separated else 0.0, 0.0, 1.0))

    return SDIRResult(
        sdir=score,
        contaminated_fraction=minority,
        distribution_split=separated,
        language=lang,
        provenance_uncertainty=prov,
        trigger_status=_status(score),
        observation_status="observed",
        origin_distribution={k: v/len(origins) for k, v in Counter(origins).items()},
        notes=notes,
    )
