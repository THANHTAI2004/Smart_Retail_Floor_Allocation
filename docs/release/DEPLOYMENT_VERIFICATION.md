# Deployment verification and missing tools

## Actual local environment

Windows 11 Pro build 26300, Acer Predator PH315-55, current shell not elevated.
HypervisorPresent=True; firmware virtualization and SLAT were reported False by
CIM inside this environment. Those flags alone do not establish BIOS support is
absent. vmcompute is running. `wsl --status` reports WSL is not installed.
Docker CLI/Desktop were initially missing.

The user explicitly authorized installing missing tools. The first WinGet
per-user selection returned No applicable installer found; a direct installer
command was rejected before execution by policy. A safer pinned WinGet invocation
with the official installer user-mode flags succeeded: Docker Desktop 4.96.1,
Docker CLI/engine 29.9.2 and Compose v5.6.0. WinGet verified the installer hash.

Microsoft.WSL 2.7.13 initially failed without administration (0x80073d28). The
same official pinned package succeeded through elevated WinGet/UAC. WSL version
2.7.13.0 and kernel 6.18.33.2-2 were verified. Docker's WSL2 backend then started
and the engine responded, without reboot or BIOS changes. No credentials were
required for tool installation. See evidence/tool-installation.json.

Installed supporting tool: npm `yaml@2.8.1`, isolated under ignored
`var/release-tools`, to parse Compose aliases and validate static invariants.
This is not a Docker runtime and does not establish image build or deployment PASS.

Docker supports a per-user installer; WSL 2 is a normal backend and has its own
Windows/virtualization prerequisites. Follow the current official
[Windows installation guide](https://docs.docker.com/desktop/setup/install/windows-install/)
and [WSL backend guide](https://docs.docker.com/desktop/features/wsl/) from a user
session able to install them. Restart only when explicitly scheduled, after saving
work and stopping application writes. This task did not reboot the computer.

## Isolated Compose procedure

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_mongodb_compose.ps1
```

The script uses a UUID Compose project, fresh DB name, random credentials,
free loopback API/web ports and project-specific named volumes. Its private .env
is stored only in ignored var. No production MongoDB instance, port or volume is
reused. It validates config, builds, starts the stack, checks authentication,
indexes, API/worker/frontend, seven input groups, T1Ã¢â‚¬â€œT4 result/report/SHA, restart
persistence, queued cancellation and expired worker recovery. It stops only its
own UUID project, retains volumes and sanitized logs, and never uses down -v.

Current Docker runtime is installed and responding. YAML parse/auth/health/volume/loopback
checks and real `docker compose config --quiet` PASS. Live isolated build and
container checks PASS in evidence/20261022-compose-06/verification.json; earlier
BLOCKED receipts are retained as history. Ports are environment-configurable.
`.dockerignore` excludes private env/keys, runtime and large generated outputs.

## Atlas procedure

Set `MONGODB_ATLAS_URI` privately in the process environment, then run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_atlas_connection.ps1
```

The dedicated URI variable authorizes a new `sr_atlas_verify_<UUID>` namespace,
not a production DB. The verifier requires Atlas SRV and validated TLS; native
PyMongo handles DNS/auth/timeouts/retry settings. It exercises indexes, application
CRUD/revision CAS, atomic queue, spawned T1Ã¢â‚¬â€œT4, checksum and reconnect readback.
Only documents created by this run in that new namespace are deleted. No existing
Atlas data is migrated or modified. Exceptions are recorded by type only to avoid
URI disclosure. The script and its live path remain unverified until credentials
and network access are supplied.

Atlas requires a database user and an allowed client IP; an Atlas web account alone
does not provide database access. See the official
[Atlas connection guide](https://www.mongodb.com/docs/atlas/connect-to-database-deployment/)
and [IP access list](https://www.mongodb.com/docs/atlas/security/add-ip-address-to-list/).
Grant the test account permissions for the intended test namespace and indexes;
never paste authenticated URIs into source/reports or disable certificate validation.

Current result: **BLOCKED_ATLAS_CREDENTIALS**. No Atlas URI was available. SRV/TLS
handling in code and secret exclusion are separate static checks, not live PASS.


Final Compose result: **PASS**. Separate docker inspect verified the MongoDB data
volume, shared API/worker artifact volume, research volume, project-specific
network and no published database port. Test stack is stopped, volumes/logs are
retained. Failed suffix-03/04 runs exposed the fresh install credential-helper PATH
issue; suffix-05 then exposed Windows default-codepage sample loading in the
verification script. The script now prepends Docker bin for buildx and explicitly
reads sample JSON as UTF-8. Suffix-06 is the final successful execution. Backend
scientific source did not change during these verifier-only corrections.
