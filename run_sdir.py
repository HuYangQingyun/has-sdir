"""
HAS-Core :: SDIR v1.1 — command-line runner
Run SDIR on your own data:

    python run_sdir.py --batch batch.json --baseline baseline.json

Each JSON file is a list of records. A batch record is:
    {"text": "...", "origin": "verified_human"}
A baseline record may be just:
    {"text": "..."}

Origin labels:
    verified_human | direct_synthetic | unknown_origin
    mixed_origin | recursive_synthetic
Missing or unrecognised origins are treated as unknown_origin.

SDIR reports DRIFT of the batch from the baseline, not a good/bad verdict.
Use a baseline matched to your batch's domain and language.

English only (current scope): this release is scoped to English-language
corpora. Do not run it on non-Latin text such as Chinese; results there are
not meaningful. See README for known open issues in v1.1.
"""
import argparse, json, sys
from has_sdir import compute_sdir, VERIFIED_HUMAN


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        sys.exit(f"{path}: expected a JSON list of records")
    return data


def main():
    p = argparse.ArgumentParser(description="HAS-Core SDIR v1.1 read-out")
    p.add_argument("--batch", required=True, help="batch JSON (text + origin)")
    p.add_argument("--baseline", required=True, help="baseline JSON (text)")
    p.add_argument("--json", action="store_true", help="machine-readable JSON output")
    args = p.parse_args()

    batch = load(args.batch); baseline = load(args.baseline)
    batch_texts   = [r["text"] for r in batch]
    batch_origins = [r.get("origin") for r in batch]        # missing -> unknown
    baseline_texts = [r["text"] for r in baseline]

    res = compute_sdir(batch_texts, batch_origins, baseline_texts)

    if args.json:
        print(json.dumps({
            "sdir": res.sdir,
            "distribution_shift": res.dist_shift,
            "lineage_concentration": res.lineage_concentration,
            "recursion_drift": res.recursion_drift,
            "diversity_drift": res.diversity_drift,
            "provenance_uncertainty": res.provenance_uncertainty,
            "status": res.trigger_status,
            "recommended_action": res.recommended_action,
            "origin_distribution": res.origin_distribution,
            "notes": res.notes,
        }, indent=2))
    else:
        print(res.as_report())


if __name__ == "__main__":
    main()
