"""
HAS-Core :: SDIR v1.1 — self-contained demonstration
Run:  python demo.py

Builds three corpora with NO external downloads:
  (A) a healthy, multi-source human-style batch      -> should read CLEAR
  (B) a recursively synthesised, inbred batch         -> should flag high drift
  (C) the SAME recursive batch with its provenance relabelled to look diverse
      -> v1.1 still flags it (v1.0 could be fooled into CLEAR here)

all scored against a human baseline. SDIR reports DRIFT FROM THE BASELINE,
not a good/bad verdict; the baseline should match the batch's domain.
"""
import random
import numpy as np
import matplotlib.pyplot as plt
from has_sdir import (compute_sdir, VERIFIED_HUMAN, DIRECT_SYNTHETIC,
    UNKNOWN_ORIGIN, MIXED_ORIGIN, RECURSIVE_SYNTH, SDIR_TRIGGER)

rng = random.Random(7)

SUBJ = ["the river delta","a copper kettle","migrating cranes","the night market",
        "an old fisherman","the granite ridge","a violin maker","monsoon clouds",
        "the harbor lights","a wheat field","the clockmaker","tidal pools",
        "a mountain pass","the printing press","desert nomads","a coral reef"]
VERB = ["weathered","unfolded across","resisted","gathered near","gave way to",
        "outlasted","drifted toward","sharpened against","receded from","held"]
TAIL = ["in the long dusk of late autumn.","before anyone thought to record it.",
        "against every prediction the elders made.","with a patience no clock keeps.",
        "as the trade winds shifted once more.","leaving only salt and rumor behind."]
def human():
    return " ".join(f"{rng.choice(SUBJ)} {rng.choice(VERB)} {rng.choice(SUBJ)} "
                    f"{rng.choice(TAIL)}" for _ in range(rng.randint(2,4)))

OPEN = ["It is important to note that","In today's fast-paced world",
        "As we can clearly see","It is worth mentioning that"]
MIDL = ["the system provides significant value","this solution enhances efficiency",
        "the approach delivers optimal results","the framework ensures scalability"]
TL   = ["in a seamless and robust manner.","to drive impactful outcomes.",
        "for a wide range of stakeholders.","moving forward into the future."]
def synth():
    return " ".join(f"{rng.choice(OPEN[:2])} {rng.choice(MIDL)} {rng.choice(TL)}"
                    for _ in range(rng.randint(2,3)))

baseline = [human() for _ in range(300)]

# A: healthy
a_txt = [human() for _ in range(300)]
a_org = [VERIFIED_HUMAN]*300

# B: recursive, honestly labelled
b_txt = [synth() for _ in range(300)]
b_org = [RECURSIVE_SYNTH]*300

# C: SAME recursive text, provenance relabelled to look diverse (EV's attack)
five = [VERIFIED_HUMAN,DIRECT_SYNTHETIC,UNKNOWN_ORIGIN,MIXED_ORIGIN,RECURSIVE_SYNTH]
c_txt = b_txt
c_org = [five[i%5] for i in range(300)]

ra = compute_sdir(a_txt, a_org, baseline)
rb = compute_sdir(b_txt, b_org, baseline)
rc = compute_sdir(c_txt, c_org, baseline)

print("\n=== A: healthy, multi-source ==="); print(ra.as_report())
print("\n=== B: recursive, honestly labelled ==="); print(rb.as_report())
print("\n=== C: SAME recursive text, provenance relabelled 'diverse' ===")
print(rc.as_report())
print("\nNote: A reads CLEAR; B flags high drift; C still flags in v1.1 even")
print("though its labels were changed to look diverse (v1.0 could be fooled).")

labels = ["dist\nshift","lineage\nconc.","recursion\ndrift","diversity\ndrift","SDIR"]
def row(r): return [r.dist_shift, r.lineage_concentration, r.recursion_drift,
                    r.diversity_drift, r.sdir]
va, vb, vc = row(ra), row(rb), row(rc)
x = np.arange(len(labels)); w = 0.26
fig, ax = plt.subplots(figsize=(9.5, 5.4))
ax.bar(x-w, va, w, label="A healthy", color="#1f9e86")
ax.bar(x,   vb, w, label="B recursive", color="#d64a3d")
ax.bar(x+w, vc, w, label="C recursive, relabelled", color="#e0913f")
ax.axhline(SDIR_TRIGGER, ls="--", lw=1, color="#444", label=f"trigger={SDIR_TRIGGER}")
ax.set_ylim(0,1.15); ax.set_ylabel("signal / score [0,1]")
ax.set_title("HAS-Core :: SDIR v1.1 — drift from baseline\n"
             "relabelling provenance no longer hides recursive drift", fontsize=12, pad=12)
ax.set_xticks(x); ax.set_xticklabels(labels); ax.legend(frameon=False, fontsize=8.5)
fig.tight_layout(); fig.savefig("sdir_demo.png", dpi=150)
print("\nFigure written to sdir_demo.png")
