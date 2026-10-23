"""Dataset confinement must use application home, not package installation depth."""

import hashlib
import runpy
from pathlib import Path

import pytest

from smart_retail.application.experiments import generators
from smart_retail.contracts.experiments import DatasetSpec
from smart_retail.infrastructure.database import ROOT


def test_imported_dataset_works_from_installed_package_location(tmp_path):
    installed = tmp_path / "site-packages/smart_retail/application/experiments/generators.py"
    installed.parent.mkdir(parents=True)
    installed.write_bytes(Path(generators.__file__).read_bytes())
    module = runpy.run_path(str(installed))
    source = ROOT / "datasets/joint/local-trap.json"
    spec = DatasetSpec(
        id="installed-import", input_path="datasets/joint/local-trap.json",
        input_file_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    )
    sections, manifest = module["generate"](spec)
    assert len(sections) == 7
    assert manifest["input_file_sha256"] == spec.input_file_sha256
    outside = spec.model_copy(update={"input_path": str(installed)})
    with pytest.raises(ValueError, match="inside the repository datasets"):
        module["generate"](outside)
