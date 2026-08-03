"""
HAS-Core :: SDIR — self-contained demonstration
Run:  python demo.py

Builds two contrasting corpora with NO external downloads:
  (A) a healthy, multi-source human-style batch
  (B) a batch undergoing synthetic inbreeding (recursive, source-collapsed)

then runs the SDIR read-out on both against a human baseline and shows that
SDIR separates them — the degradation is caught before any model sees it.
"""

import random
import numpy as np
import matplotlib.pyplot as plt

from has_sdir import (
    compute_sdir,
    VERIFIED_HUMAN, DIRECT_SYNTHETIC, UNKNOWN_ORIGIN,
    MIXED_ORIGIN, RECURSIVE_SYNTH,
    SDIR_TRIGGER,
)

rng = random.Random(7)

# ----------------------------------------------------------------------
# Vocabulary pools — the healthy pool has a long tail; the collapsed pool
# reuses a narrow set of tokens and templates (the inbreeding signature).
# ----------------------------------------------------------------------
HUMAN_SUBJECTS = [
    "the river delta", "a copper kettle", "migrating cranes", "the night market",
    "an old fisherman", "the granite ridge", "a violin maker", "monsoon clouds",
    "the harbor lights", "a wheat field", "the clockmaker", "tidal pools",
    "a mountain pass", "the printing press", "desert nomads", "a coral reef",
]
HUMAN_VERBS = [
    "weathered", "unfolded across", "resisted", "gathered near", "gave way to",
    "outlasted", "drifted toward", "sharpened against", "receded from", "held",
]
HUMAN_TAILS = [
    "in the long dusk of late autumn.", "before anyone thought to record it.",
    "against every prediction the elders made.", "with a patience no clock keeps.",
    "as the trade winds shifted once more.", "leaving only salt and rumor behind.",
    "the way forgotten crafts sometimes do.", "under a sky the color of slate.",
]

SYNTH_OPENERS = [
    "It is important to note that", "In today's fast-paced world",
    "As we can clearly see", "It is worth mentioning that",
]
SYNTH_MIDDLE = [
    "the system provides significant value", "this solution enhances efficiency",
    "the approach delivers optimal results", "the framework ensures scalability",
]
SYNTH_TAILS = [
    "in a seamless and robust manner.", "to drive impactful outcomes.",
    "for a wide range of stakeholders.", "moving forward into the future.",
]


def make_human_doc() -> str:
    parts = []
    for _ in range(rng.randint(2, 4)):
        parts.append(
            f"{rng.choice(HUMAN_SUBJECTS)} {rng.choice(HUMAN_VERBS)} "
            f"{rng.choice(HUMAN_SUBJECTS)} {rng.choice(HUMAN_TAILS)}"
        )
    return " ".join(parts)


def make_synth_doc(depth: int) -> str:
    """Higher depth = more recursive collapse: fewer openers, more repetition."""
    opener_pool = SYNTH_OPENERS[: max(1, 4 - depth)]
    parts = []
    for _ in range(rng.randint(2, 3)):
        parts.append(
            f"{rng.choice(opener_pool)} {rng.choice(SYNTH_MIDDLE)} "
            f"{rng.choice(SYNTH_TAILS)}"
        )
    return " ".join(parts)


# ----------------------------------------------------------------------
# Corpora
# ----------------------------------------------------------------------
baseline = [make_human_doc() for _ in range(300)]

# Batch A: healthy, multi-source
batch_a_texts   = [make_human_doc() for _ in range(300)]
batch_a_origins = [rng.choice(
    [VERIFIED_HUMAN, VERIFIED_HUMAN, VERIFIED_HUMAN, MIXED_ORIGIN, UNKNOWN_ORIGIN]
) for _ in range(300)]

# Batch B: synthetic inbreeding — source-collapsed, deeply recursive
batch_b_texts   = [make_synth_doc(depth=3) for _ in range(300)]
batch_b_origins = [rng.choice(
    [RECURSIVE_SYNTH, RECURSIVE_SYNTH, RECURSIVE_SYNTH, DIRECT_SYNTHETIC]
) for _ in range(300)]

res_a = compute_sdir(batch_a_texts, batch_a_origins, baseline)
res_b = compute_sdir(batch_b_texts, batch_b_origins, baseline)

print("\n=== BATCH A (healthy, multi-source) ===")
print(res_a.as_report())
print("\n=== BATCH B (synthetic inbreeding) ===")
print(res_b.as_report())

# ----------------------------------------------------------------------
# Figure
# ----------------------------------------------------------------------
labels = ["dist.\nshift", "lineage\nconc.", "recursion\nfinger.",
          "diversity\ncontr.", "SDIR"]
vals_a = [res_a.dist_shift, res_a.lineage_concentration,
          res_a.recursion_fingerprint, res_a.diversity_contraction, res_a.sdir]
vals_b = [res_b.dist_shift, res_b.lineage_concentration,
          res_b.recursion_fingerprint, res_b.diversity_contraction, res_b.sdir]

x = np.arange(len(labels))
w = 0.38
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.bar(x - w/2, vals_a, w, label="Batch A — healthy", color="#3a7d5d")
ax.bar(x + w/2, vals_b, w, label="Batch B — inbreeding", color="#b5493a")
ax.axhline(SDIR_TRIGGER, ls="--", lw=1, color="#444",
           label=f"SDIR trigger = {SDIR_TRIGGER}")
ax.set_ylim(0, 1.18)
ax.set_yticks(np.linspace(0, 1.0, 6))
ax.set_ylabel("normalised signal  [0, 1]")
ax.set_title("HAS-Core :: SDIR — formative-layer read-out\n"
             "degradation caught before the model trains on it",
             fontsize=12, pad=14)
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(frameon=False, fontsize=9)
for i, v in enumerate(vals_a):
    ax.text(i - w/2, v + 0.02, f"{v:.2f}", ha="center", fontsize=8)
for i, v in enumerate(vals_b):
    ax.text(i + w/2, v + 0.02, f"{v:.2f}", ha="center", fontsize=8)
fig.tight_layout()
fig.savefig("sdir_demo.png", dpi=150)
print("\nFigure written to sdir_demo.png")
