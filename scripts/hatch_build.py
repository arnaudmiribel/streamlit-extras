"""Hatchling build hook for building CCv2 React component frontends.

This hook automatically builds all React-based CCv2 extras during the wheel build process,
ensuring the compiled JS bundles are included without requiring a separate build step.

Note: This file duplicates some logic from build_frontends.py because build hooks
run in an isolated environment and cannot import local modules.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

EXTRAS_DIR = Path("src/streamlit_extras")
SHARED_MANIFEST = EXTRAS_DIR / "pyproject.toml"


class FrontendBuildHook(BuildHookInterface):
    """Build hook that compiles React frontends before wheel packaging."""

    PLUGIN_NAME = "frontend-build"

    def initialize(self, _version: str, build_data: dict[str, Any]) -> None:
        """Build all React CCv2 frontends before the wheel is packaged."""
        extras = self._find_react_extras()

        if not extras:
            return

        print(f"Building {len(extras)} React CCv2 frontend(s)...")

        for extra_dir in extras:
            self._build_frontend(extra_dir)

        self._update_shared_manifest(extras)

        # Explicitly mark the generated build artifacts so hatchling includes
        # them in the wheel even though they are listed in .gitignore.
        for extra_dir in extras:
            build_data["artifacts"].append(
                f"{EXTRAS_DIR}/{extra_dir.name}/frontend/build/**"
            )

    def _find_react_extras(self) -> list[Path]:
        """Find all React-based CCv2 extras."""
        react_extras = [package_json.parent.parent for package_json in EXTRAS_DIR.glob("*/frontend/package.json")]
        return sorted(react_extras)

    def _build_frontend(self, extra_dir: Path) -> None:
        """Build the frontend for a single React CCv2 extra."""
        extra_name = extra_dir.name
        frontend_dir = extra_dir / "frontend"
        build_dir = frontend_dir / "build"

        print(f"  Building: {extra_name}")

        if build_dir.exists():
            shutil.rmtree(build_dir)

        lock_file = frontend_dir / "package-lock.json"
        install_cmd = ["npm", "ci"] if lock_file.exists() else ["npm", "install"]
        subprocess.run(install_cmd, cwd=frontend_dir, check=True, capture_output=True)
        subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True, capture_output=True)

        js_files = list(build_dir.glob("index-*.js"))
        if len(js_files) != 1:
            raise RuntimeError(f"{extra_name}: expected 1 JS file, found {len(js_files)}")

        print(f"    OK: {js_files[0].name}")

    def _update_shared_manifest(self, extras: list[Path]) -> None:
        """Update the shared pyproject.toml manifest."""
        entries = [
            f"[[tool.streamlit.component.components]]\n"
            f'name = "{extra_dir.name}"\n'
            f'asset_dir = "{extra_dir.name}/frontend/build"'
            for extra_dir in extras
        ]

        content = (
            "# CCv2 component manifest for react-based extras\n"
            "# Auto-generated during build - do not edit manually!\n"
            "\n"
            "[project]\n"
            'name = "streamlit-extras"\n'
            'version = "0.0.1"\n'
            "\n"
            f"{chr(10).join(entries)}\n"
        )

        SHARED_MANIFEST.write_text(content)
        print(f"  Updated manifest with {len(extras)} component(s)")
