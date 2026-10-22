# Final release acceptance ? 2026-10-22

**RELEASE_READY_WITH_EXTERNAL_BLOCKERS**. No required local test failure remains.
Atlas live access is blocked; Docker/WSL installation and real isolated Compose PASS.

Every gate has command, UTC timestamp, environment, exit code, evidence, failure
reason and blocker in [machine-readable matrix](evidence/release-acceptance.json).
Statuses below describe actual execution, not planned coverage.

| Gate | Requirement | Status | Evidence / limitation |
|---|---|---|---|
| WL01 | Root cause reproduced | PASS | docs/release/evidence/20261022-longpath-baseline/cache-reproduction.json |
| WL02 | Safe shared filesystem path handling | PASS | docs/release/evidence/20261022-longpath-03/verification.json |
| WL03 | Deep Unicode native file I/O | PASS | docs/release/evidence/20261022-longpath-03/verification.json |
| WL04 | Atomic no-overwrite cache publication | PASS | docs/release/evidence/20261022-longpath-03/verification.json |
| WL05 | Concurrent cache access | PASS | docs/release/evidence/20261022-longpath-03/verification.json |
| WL06 | Spawned worker/subprocess paths | PASS | docs/release/evidence/20261022-longpath-03/verification.json |
| WL07 | Long-path regression cases | PASS | docs/release/evidence/20261022-longpath-03/verification.json |
| WL08 | Full backend long and short | PASS | docs/release/evidence/20261022-longpath-03/verification.json |
| DC01 | Compose config validation | PASS | docs/release/evidence/20261022-compose-06/verification.json |
| DC02 | Real backend/frontend image builds | PASS | docs/release/evidence/20261022-compose-06/verification.json |
| DC03 | Isolated authenticated MongoDB startup | PASS | docs/release/evidence/20261022-compose-06/verification.json |
| DC04 | Unauthenticated access rejected | PASS | docs/release/evidence/20261022-compose-06/verification.json |
| DC05 | API and worker indexes/integration | PASS | docs/release/evidence/20261022-compose-06/verification.json |
| DC06 | Data persistence across restart | PASS | docs/release/evidence/20261022-compose-06/verification.json |
| DC07 | Real seven-input T1-T4/result/report/checksum + cancellation/recovery | PASS | docs/release/evidence/20261022-compose-06/verification.json |
| DC08 | Actual volume/network/port isolation | PASS | docs/release/evidence/compose-isolation.json |
| AT01 | Atlas SRV/TLS live configuration | BLOCKED | docs/release/evidence/20261022-atlas-01/verification.json ? BLOCKED_ATLAS_CREDENTIALS |
| AT02 | Atlas authentication | BLOCKED | docs/release/evidence/20261022-atlas-01/verification.json ? BLOCKED_ATLAS_CREDENTIALS |
| AT03 | Isolated Atlas database access | BLOCKED | docs/release/evidence/20261022-atlas-01/verification.json ? BLOCKED_ATLAS_CREDENTIALS |
| AT04 | Atlas CRUD | BLOCKED | docs/release/evidence/20261022-atlas-01/verification.json ? BLOCKED_ATLAS_CREDENTIALS |
| AT05 | Atlas atomic queue | BLOCKED | docs/release/evidence/20261022-atlas-01/verification.json ? BLOCKED_ATLAS_CREDENTIALS |
| AT06 | No credential disclosure in staged blobs | PASS | docs/release/evidence/git-audit-01/staged-audit.json |
| GT01 | Full source inventory | PASS | docs/release/GIT_SOURCE_INVENTORY.md |
| GT02 | Required source tracked | PASS | docs/release/GIT_SOURCE_INVENTORY.md |
| GT03 | Generated output retention/ignore policy | PASS | docs/release/GIT_SOURCE_INVENTORY.md |
| GT04 | Secrets excluded | PASS | docs/release/GIT_SOURCE_INVENTORY.md |
| GT05 | Concrete git check-ignore assertions | PASS | docs/release/GIT_SOURCE_INVENTORY.md |
| GT06 | Staged diff/blob audit | PASS | docs/release/GIT_SOURCE_INVENTORY.md |
| GT07 | Authorized local checkpoint committed | PASS | docs/release/evidence/git-audit-01/local-checkpoint.json |
| GT08 | Clean tracked/untracked release status | PASS | docs/release/evidence/git-audit-01/local-checkpoint.json |
| GT09 | Clean-environment setup documented | PASS | docs/release/GIT_SOURCE_INVENTORY.md |
| GT10 | Scientific artifacts preserved externally | PASS | docs/release/evidence/research-preservation.json |
| QA01 | Ruff | PASS | docs/release/evidence/20261022-release-quality-01/verification.json |
| QA02 | mypy | PASS | docs/release/evidence/20261022-release-quality-01/verification.json |
| QA03 | Backend pytest 171 pass / 0 failures / 0 skips | PASS | docs/release/evidence/20261022-release-quality-01/verification.json |
| QA04 | Vitest 4 pass | PASS | docs/release/evidence/20261022-release-quality-01/verification.json |
| QA05 | ESLint | PASS | docs/release/evidence/20261022-release-quality-01/verification.json |
| QA06 | Frontend build | PASS | docs/release/evidence/20261022-release-quality-01/verification.json |
| QA07 | Playwright 9 pass | PASS | docs/release/evidence/20261022-release-quality-01/verification.json |
| QA08 | MongoDB health / worker online | PASS | docs/release/evidence/local-data-and-science.json |
| QA09 | New sequential/feedback/exact campaign and independent proof | PASS | docs/release/evidence/20261022-proof-command.json |
| QA10 | New scientific replay 3/3 input/result SHA and numeric equivalence | PASS | experiments/reports/20261022-release-joint-comparison-01.json |

Totals: 37 PASS, 0 FAIL, 5 BLOCKED.

Additional scope: live UNC filesystem NOT_APPLICABLE (no share); remote CI not
executed. Neither is silently represented as runtime PASS. Atlas test access is
the remaining mandatory external gate; software installation cannot create
authorized cluster credentials.

Local source checkpoint: `cbe15bb9dc5fcb4d1de1f3949ee4855159699b9c`. Final documentation is recorded in a follow-up
local checkpoint. No GitHub push, reset, clean, amend or history rewrite.
Raw generated results remain ignored locally with verified external archive.
Final Git/clean-state confirmation is in the closeout receipt and local Git log.
