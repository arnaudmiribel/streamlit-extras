"""Regression checks for dependency and automation configuration."""

import json
import re
import sys
from pathlib import Path

import pytest
import yaml

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]
FRONTENDS = sorted((ROOT / "src/streamlit_extras").glob("*/frontend/package.json"))
WORKFLOWS = sorted((ROOT / ".github/workflows").glob("*.yml"))


@pytest.mark.parametrize("manifest_path", FRONTENDS, ids=lambda path: path.parent.parent.name)
def test_frontend_lock_matches_manifest_when_tracked(manifest_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    lock_path = manifest_path.with_name("package-lock.json")
    if not lock_path.exists():
        return

    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    root = lock["packages"][""]
    assert root["name"] == manifest["name"]
    assert root["version"] == manifest["version"]
    assert root["dependencies"] == manifest["dependencies"]
    assert root["devDependencies"] == manifest["devDependencies"]


@pytest.mark.parametrize("workflow_path", WORKFLOWS, ids=lambda path: path.stem)
def test_github_actions_use_versioned_releases(workflow_path: Path) -> None:
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
    for job in workflow.get("jobs", {}).values():
        for step in job.get("steps", []):
            action = step.get("uses")
            if action:
                assert re.fullmatch(r"[\w-]+/[\w-]+@v\d+\.\d+\.\d+", action)


def test_python_dev_dependencies_keep_toolchain_compatible() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = project["dependency-groups"]["dev"]
    assert "numpy<2.5" in dependencies
    assert "mypy==2.1.0" in dependencies
    assert "ty==0.0.74" in dependencies
    assert "ruff==0.16.5" in dependencies

    precommit = yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8"))
    ruff = next(repo for repo in precommit["repos"] if repo["repo"].endswith("/ruff-pre-commit"))
    assert ruff["rev"] == "v0.16.5"
