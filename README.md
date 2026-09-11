HAS-Core :: SDIR
SDIR — Synthetic Data Inbreeding Rate. A read-only, lightweight diagnostic for the integrity of AI data. It examines a batch of documents and reports the degree to which the batch shows signs of synthetic-data contamination consistent with recursive (“inbreeding”) reuse.
Part of HAS-Core. SDIR is one module of the HAS-Core AI-safety system — a family of read-only, lightweight, statistical safety modules. This repository covers the SDIR module only.
License: Non-Commercial Research only. Free for research and study. Commercial use requires prior written permission — see LICENSE.
SDIR is a data-integrity read-out for use across the full AI lifecycle — not only at the point of training. Wherever AI data flows, it can be read for signs of synthetic contamination:
• in live and deployed systems, where models are continuously fed, retrieved-against, and re-grounded on data of mixed and often unknown provenance — the setting where contamination does the most quiet damage, and where SDIR is most useful in practice;
• in evaluation and monitoring, as an integrity read-out on the data a system is being judged on or is judging with;
• upstream, on data before it enters training.
Contamination is not a one-time gate at training; it recurs wherever AI data is reused. In real deployments the downstream stages matter most — a compromised data stream in a running system is harder to see, and costlier to ignore, than one caught on a bench.
This repository is a public demonstration and test harness. Its purpose is to make the direction visible and runnable, so the effect can be seen:
• Read-only — it reports evidence, it does not decide. A diagnosis is evidence; a separate policy layer decides.
• Multilingual — automatic language detection across English, Chinese, French, Spanish and German.
• Deterministic and honest under edge conditions (see below).
The detection core is not part of this public build. This repository demonstrates the effect; the working method is not included here.
A separate, engineering-grade edition — internally at 3.0 — reaches materially higher performance on real-world data: AUC ≈ 0.90 (honest average over many runs), using lightweight statistics (no GPU, no model). This edition is not published.
It is complete and available only through direct collaboration or commercial licensing. This public build shows the direction and the level reached; the engineering edition is the production instrument.
We are currently raising a pre-seed round, and are seeking angel investors and capable, well-resourced partners — institutions and individuals with the strength, resources, and track record to build at scale — to test and validate, to deploy the engineering edition, and to pursue joint reporting and enterprise development. Our one firm condition is that we keep control of our technical and innovation path; beyond that, terms and structure are open. This is an open invitation, and we welcome conversations to explore it.
Modern AI increasingly reuses AI-generated data. Training and re-grounding successive systems on synthetic data drives recursive degradation — the output distribution narrows and diversity collapses (“model collapse”). And it does not end at training: deployed systems ingest, retrieve, and recycle data of unknown origin continuously, so contamination re-enters downstream, where it is hardest to see.
SDIR gives a provenance-integrity read-out on the data itself — wherever that data sits in the lifecycle. It complements model-evaluation work and sits alongside it, not instead of it.
Given a batch of documents, SDIR returns:
• a contamination read-out (an SDIR score),
• a graded status — CLEAR / MONITOR / REVIEW / SEVERE-DRIFT,
• separate observation states for cases where a clean reading cannot be given (see “Honest behaviour” below).
SDIR is a batch-contamination diagnostic: it reports how far a batch shows signs of synthetic contamination as a whole. It is not a single-document AI-text classifier — it does not claim to decide whether one specific document was AI-written. Tools such as DetectGPT or GPTZero address that different task.
As a lightweight statistical read-out, SDIR is deliberately general, not domain-specific. Highly formulaic or narrowly templated text — in any single domain — can sit close to the line for lightweight methods generally. Where a particular domain matters, the right answer is a calibrated layer built for that domain, added on request — not the general tool stretched to fit.
The read-out is built not to overclaim:
• Small samples return an insufficient / UNOBSERVED status — “cannot observe” is never reported as “nothing wrong”.
• Unknown provenance is reported as its own state and does not by itself raise the contamination score — unknown is not treated as dangerous.
• Deterministic — the same input gives the same read-out.
• BaselineLock — a reference set cannot be silently swapped or loosened without an operator-supplied secret.
• has_sdir.py — the public demonstration read-out
• multilang.py — multilingual tokenization (en, zh, fr, es, de)
• demo.py — runnable demonstration
• LICENSE — non-commercial research license
from has_sdir import compute_sdir, VERIFIED_HUMAN
result = compute_sdir(batch_texts, batch_origins, baseline_texts)
print(result.as_report())
Harmondeg Institute for Philosophy & Practice (HIPP)
Qingyun Hu-Yang · Calgary, Alberta, Canada
Tel: +1 403 702 6608
Email: contact@harmondeg.org / huqingyun@hotmail.com
GitHub: https://github.com/HuYangQingyun/has-sdir

