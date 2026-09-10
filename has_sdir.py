"""
HAS-Core :: SDIR  (public demonstration build)

Synthetic Data Inbreeding Rate — a read-only diagnostic that examines a batch of
documents and reports the degree to which the batch shows signs of synthetic-data
contamination consistent with recursive ("inbreeding") reuse.

This is a PUBLIC DEMONSTRATION build. It is provided so the effect can be seen
and exercised. It reports evidence; it does not decide. The detection core is a
black box in this build: a result is produced, but the working method is not
included here.

A separate engineering edition (internally at 3.0) reaches materially higher
performance on real-world data. That edition is NOT published — see the README
for what it reaches and how to engage.

Interface:  compute_sdir(batch_texts, batch_origins, baseline_texts)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter
import hashlib

from multilang import tokenize_batch
from _core import read_out   # detection core — not disclosed in the public build

# ---- provenance labels ----
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

MIN_OBSERVABLE = 10   # below this, a distribution cannot be observed


def _stable_fingerprint(texts) -> str:
    """Stable, order-sensitive fingerprint of a text set (SHA-256), so a
    reference set is reproducible across runs and cannot be silently altered."""
    h = hashlib.sha256()
    for t in texts:
        h.update(t.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


@dataclass
class BaselineLock:
    """A reference baseline fixed once and not silently swappable. Replacing it
    requires an operator-supplied secret; it is never hardcoded."""
    texts: list
    auth_secret: str = None
    _fingerprint: str = field(default="")

    def __post_init__(self):
        self._fingerprint = _stable_fingerprint(self.texts)

    def verify(self, presented_texts) -> bool:
        return _stable_fingerprint(presented_texts) == self._fingerprint

    def authorise_replacement(self, new_texts, secret=None):
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

    def as_report(self) -> str:
        L = [
            "HAS-Core :: SDIR read-out (public demonstration build)",
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


def _status(s):
    if s < SDIR_MONITOR: return "CLEAR"
    if s < SDIR_TRIGGER:  return "MONITOR"
    if s < SDIR_SEVERE:   return "REVIEW"
    return "SEVERE-DRIFT"


def compute_sdir(batch_texts, batch_origins, baseline_texts):
    """Read a batch for signs of synthetic contamination.

    Multilingual: language is detected automatically. The baseline may be wrapped
    in a BaselineLock. Observation status is reported separately from the score:
    too few documents yields 'insufficient' (not a clean reading). Provenance
    uncertainty is its own state and is not folded into the score.
    """
    if len(batch_texts) != len(batch_origins):
        raise ValueError("batch_texts and batch_origins must align 1:1")
    if len(batch_texts) < 2 or len(baseline_texts) < 2:
        raise ValueError("need >=2 docs in batch and baseline")

    origins, notes = _normalise_origins(batch_origins)
    prov = _provenance_uncertainty(origins)
    token_lists, lang = tokenize_batch(batch_texts)

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

    # ---- detection core: sealed in the public build ----
    # The public build reports from the provenance labels supplied with the
    # batch; the working detector is not part of this build.
    separated, minority = read_out(origins)
    score = float(min(max(minority * 1.6 if separated else 0.0, 0.0), 1.0))

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
