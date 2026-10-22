# Reproducibility

From repository root, use the new .venv rather than a retired environment:

```powershell
.venv\Scripts\python.exe experiments/run_campaign.py --output experiments/results/my-new-campaign --seeds 11,23,37,53,71
.venv\Scripts\python.exe experiments/analyze_campaign.py experiments/results/my-new-campaign
```

Output directories must not exist. Each run uses the production durable queue in a dedicated SQLite database, a killable process, full snapshots and source/dependency identity.

```powershell
.venv\Scripts\python.exe experiments/run_campaign.py --output experiments/results/my-new-replay --replay experiments/results/20261021-research-02/artifacts/bbef0fbf-e729-472e-8bfe-edf6e20e8c1e/input.json
```

Replay refuses a changed source/dependency identity. Verified replay: bbef0fbf-e729-472e-8bfe-edf6e20e8c1e to f2bdc86c-e28e-44e1-8965-324ff475ac42, with identical input/result hashes. No cross-platform/cross-solver bitwise guarantee is claimed. Existing analysis.json is never overwritten.

configuration.json records generator/source/package identities. analysis.json hashes all campaign JSON and independently audits physical constraints/routes. Per-envelope contract versions and complete API run start/end auditing remain absent; GATE 08 is incomplete.
