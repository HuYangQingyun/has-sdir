"""
HAS-Core :: SDIR — command-line runner
Run SDIR on your own data:

    python run_sdir.py --batch batch.json --baseline baseline.json

Each JSON file is a list of records. A batch record is:
    {"text": "...", "origin": "verified_human"}
A baseline record may be just:
    {"text": "..."}

Origin labels:
    verified_human | direct_synthetic | unknown_origin
    mixed_origin | recursive_synthetic
"""

import argparse
import json
import sys

from has_sdir import compute_sdir, VERIFIED_HUMAN


def load(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        sys.exit(f"{path}: expected a JSON list of records")
    return data


def main() -> None:
    p = argparse.ArgumentParser(description="HAS-Core SDIR read-out")
    p.add_argument("--batch", required=True, help="batch JSON (text + origin)")
    p.add_argument("--baseline", required=True, help="human baseline JSON (text)")
    p.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = p.parse_args()

    batch = load(args.batch)
    baseline = load(args.baseline)

    batch_texts   = [r["text"] for r in batch]
    batch_origins = [r.get("origin", VERIFIED_HUMAN) for r in batch]
    baseline_texts = [r["text"] for r in baseline]

    res = compute_sdir(batch_texts, batch_origins, baseline_texts)

    if args.json:
        print(json.dumps({
            "sdir": res.sdir,
            "distribution_shift": res.dist_shift,
            "lineage_concentration": res.lineage_concentration,
            "recursion_fingerprint": res.recursion_fingerprint,
            "diversity_contraction": res.diversity_contraction,
            "trigger_status": res.trigger_status,
            "recommended_action": res.recommended_action,
            "origin_distribution": res.origin_distribution,
        }, indent=2))
    else:
        print(res.as_report())


if __name__ == "__main__":
    main()
