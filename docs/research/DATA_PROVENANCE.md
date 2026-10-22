# Data provenance

All new campaign data is SYNTHETIC. The [dataset manifest](../../datasets/manifest-research-v1.json) records source, bundle version, units, transformations, fixture/schema hashes, rights assertions and limitations. Retired research documents or legacy results are not evidence for the new engines.

Every run retains input.json with runtime identity, input hash, result.json or error.json, receipt and result hash. Campaign configuration records generator hash, original sample hash, seeds and platform. The UI configuration fields were added to the working sample after the campaign started; immutable per-run input snapshots remain authoritative. Historical hashes have not been rewritten to match the current sample.

S05 measured floorplan/pickup/reference paths are unavailable. S06 verified real source/version/usage rights are unavailable. S07 measured shelf/SKU dimensions and independent field capacity audit are unavailable. These are BLOCKED_EXTERNAL_EVIDENCE for REAL_WORLD_VALIDATED. No observations or real calibration are asserted.

The bundle version lives in a manifest. Per-envelope contract versions are still missing and remain a GATE 02 gap.
