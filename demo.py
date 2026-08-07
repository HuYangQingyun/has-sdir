"""SDIR v2.0 demonstration. Shows the distribution view detecting and
quantifying mid-range contamination on realistic data, and reading a clean
batch as clear. Run: python demo.py"""
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
print("SDIR v2.0 demonstration (realistic data)")
print("="*60)

# clean batch
random.seed(1)
clean=[human() for _ in range(200)]
r=compute_sdir(clean, [VERIFIED_HUMAN]*200, baseline)
print("\n[1] Clean human batch:")
print(r.as_report())

# ~30% synthetic
random.seed(2)
mixed=[synth() for _ in range(60)]+[human() for _ in range(140)]
random.shuffle(mixed)
r=compute_sdir(mixed, [VERIFIED_HUMAN]*200, baseline)
print("\n[2] Batch ~30% synthetic:")
print(r.as_report())
