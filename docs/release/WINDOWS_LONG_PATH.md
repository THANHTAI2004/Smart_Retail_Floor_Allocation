# Windows long-path root cause and fix

The pre-fix cache module was replayed directly from the verified pre-edit source
archive. A cache directory of 244 characters was created, then writing the UUID
temporary file of 286 characters raised FileNotFoundError at Path.write_text.
Previously only os.link arguments received extended-length conversion. Cache
directory creation, exists/read/write/unlink and other artifact paths did not.
This reproduces the reported defect independently of pytest's own directory setup.

An initial baseline with an ordinary 314-character pytest base failed even earlier
inside pytest mkdir. The verification runner now creates only the **parent** with
the shared normalizer and supplies an extended base to pytest, whose own base mkdir
is not recursive. This is test harness setup, not the application fix: regression
tests also pass ordinary unprefixed paths >330 characters directly to StageCache.

`infrastructure/filesystem.py` normalizes absolute owned roots on Windows to
drive/UNC extended-length paths, rejects device/relative Windows forms, preserves
Unicode, and leaves POSIX native. Derived paths inherit that prefix for all I/O.
`logical_fs_path` retains the old path spelling used to derive campaign database
identity, avoiding an accidental new queue when resuming an existing campaign.

Covered boundaries: StageCache; worker artifacts/progress/child spawn; experiment
storage, campaign roots/locks, HTTP research home/report download paths; CSV/figure
reports; replay comparison and independent certificate CLI input/output.
No numerical algorithm, cache envelope, key or scientific checksum format changed.

Cache publication still uses atomic no-overwrite hard link after completing the
temporary file. Existing cache wins a race. Temporary files are removed in finally,
including publication/write failure. Unsupported hard links raise a clear OS error;
there is no unsafe overwrite fallback. Readback verifies the existing SHA contract.
The contract guarantees atomic visibility/immutability, not fsync-level power-loss
durability. Mutable checkpoints still use atomic replacement with Windows sharing
violation retries. Scientific immutable JSON now also publishes complete files via
the same no-overwrite primitive.

New regression cases cover short/deep Unicode paths, repeat read/write, existing
cache, checksum corruption, 32 concurrent writers, unsupported-link failure,
cleanup, immutable/mutable JSON, drive/UNC syntax, extended-path roundtrip and
spawned subprocess. Full-suite worker tests exercise real Windows spawn and deep
report export/download. UNC syntax is tested; no accessible UNC test share was
provided, so live UNC filesystem semantics are NOT_APPLICABLE, not claimed PASS.

Run `scripts/verify_windows_long_path.ps1`. Final receipt:
`evidence/20261022-longpath-03/verification.json`: full backend **171 PASS** at a
350-character logical base, **171 PASS** at a 50-character base, then both reported
HTTP cases PASS in each of three independent deep-path runs. Zero MongoDB skips.

Earlier evidence directories are retained: suffix-01 failed because the harness
had not created pytest's parent; suffix-02 exposed a new-test comparison between
logical and prefixed spelling (corrected to compare normalized identities), and
one HTTP repeat crossed a source-edit boundary. Final suffix-03 ran after source
freeze and supersedes those attempts. No existing assertion was weakened or skipped.
