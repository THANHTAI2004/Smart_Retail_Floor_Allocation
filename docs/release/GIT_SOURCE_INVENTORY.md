# Git source inventory — 2026-10-22

Repository: D:/Smart_Retail_Floor_Allocation. Baseline HEAD:
85add59f11ca48265e7613c9f09747b80eaaec3b, branch main. Existing dirty work included
the previously requested MongoDB-only retirement, not unrelated user source.
The release includes that prerequisite and the filesystem/deployment verification
changes; no engine optimization model has been rewritten.

| Classification | Paths | Policy |
|---|---|---|
| Source | backend/src, frontend/src, experiments/run_campaign.py, experiments/visualization, scripts | Version control |
| Tests | backend/tests, frontend/tests | Version control |
| Configuration/contracts | backend/pyproject.toml, requirements-lock.txt, frontend/package-lock.json, datasets/schemas, datasets/joint, experiments/configs, Dockerfiles, Compose, .env.example, .github | Version control; examples have placeholders only |
| Evidence | docs, HANDOFF.md, experiments/reports | Retain published historical reports and release receipts in Git |
| Generated research runs | experiments/results/*/ | Keep local, ignore new runs; verified external archive + SHA manifest |
| Runtime | var/artifacts, var/research, var/mongodb, var/tools, logs, venvs | Keep local; never stage |
| Sensitive | .env, .env.local, .env.*.local, private MongoDB URI, keys | Exclude from Git and Docker build context |
| Original research documents | Retail_TestPack, docx, de-cuong, HANDOFF.html and historical assets | Preserve; no broad deletion or new classification as runtime source |
| Retired SQL | SQL adapters/importer/tests, Alembic files, old tracked campaign.db | Stage verified removals; external backup and decoded MongoDB history already verified |

`.gitignore` excludes generated **results**, not the entire experiments directory.
Configs, report source, fixed datasets and research documentation remain visible.
Already tracked historical JSON is preserved. Old tracked SQL database deletions
belong to the user's explicit MongoDB-only request. The scientific JSON manifests
do not include campaign.db and remain valid without it.

Audit commands: git status --short; git diff --stat; git ls-files;
git ls-files --others --exclude-standard; git check-ignore -v --no-index.
Command output, candidate SHA manifest, private-URI/token/key scan and concrete
ignore-rule assertions: `evidence/git-audit-01/`. The broad initial candidate
manifest is historical inventory, not a claim that later report bytes are unchanged.
The final staged audit records staged blob scan and count separately.

Raw campaign bytes are preserved externally, with per-file SHA-256 and ZIP-member
readback: `evidence/research-preservation.json`. No research result is deleted to
make Git status clean. Runtime package/tool installations are outside tracked source.
Tool installation did not change backend runtime dependency identity.

The user previously authorized Git commit operations; this prompt explicitly
prohibits GitHub push. Only a reviewed **local** release checkpoint is permitted.
No reset, clean, amend, history rewrite, force push or remote push is used.
