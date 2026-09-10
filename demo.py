"""SDIR demonstration (public build).

Shows the intended read-out: a clean batch reads CLEAR, a contaminated batch
reads REVIEW. The public build reports from the provenance labels supplied with
each batch — the detection core is sealed (not disclosed), so this demonstrates
the effect and the reporting, not the method. Run: python demo.py
"""
import random
from has_sdir import compute_sdir, VERIFIED_HUMAN, RECURSIVE_SYNTH

HW=("harbor kettle cranes fisherman ridge violin clouds pools nomads delta market reef wheat "
    "pass river mountain forest desert ocean valley whisper thunder amber crimson silver ancient "
    "weathered fragile luminous gather scatter drift resist outlast recede sharpen dissolve emerge "
    "memory rumor season migration harvest tide current wind salt stone copper granite slate timber "
    "willow cedar autumn winter monsoon dusk dawn patience elder record trade horizon lantern").split()
def human(): return ' '.join(random.choice(HW) for _ in range(random.randint(12,22)))
AO=["it is important to note that","in today's rapidly evolving landscape","as we can clearly observe"]
AM=["the system provides significant value","this approach delivers optimal results","the framework ensures robust scalability"]
AE=["in a seamless and effective manner","to maximize stakeholder engagement","for sustainable long-term growth"]
def synth(): return ' '.join(f"{random.choice(AO)} {random.choice(AM)} {random.choice(AE)}" for _ in range(random.randint(2,3)))

random.seed(0)
baseline=[human() for _ in range(100)]

print("="*60)
print("SDIR demonstration (public build)")
print("="*60)

# clean batch: all human-origin
random.seed(1)
clean=[human() for _ in range(200)]
clean_origins=[VERIFIED_HUMAN]*200
r=compute_sdir(clean, clean_origins, baseline)
print("\n[1] Clean human batch:")
print(r.as_report())

# ~30% synthetic batch, carrying honest provenance labels
random.seed(2)
docs   = [synth() for _ in range(60)] + [human() for _ in range(140)]
origins= [RECURSIVE_SYNTH]*60         + [VERIFIED_HUMAN]*140
pairs=list(zip(docs, origins)); random.shuffle(pairs)
docs, origins = [p[0] for p in pairs], [p[1] for p in pairs]
r=compute_sdir(docs, origins, baseline)
print("\n[2] Batch ~30% synthetic:")
print(r.as_report())

print("\n" + "-"*60)
print("Note: this is a demonstration of the effect and the reporting. The")
print("detection core is not part of the public build. To evaluate your own")
print("data with the engineering edition, contact the Harmondeg Institute")
print("(see README).")
