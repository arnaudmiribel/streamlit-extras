import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PAGES = (
    "index.md",
    "getting_started.md",
    "extras/index.md",
    "contributing.md",
    "agents.md",
)


@pytest.mark.parametrize("page", PAGES)
def test_docs_internal_links_resolve(page: str) -> None:
    source = DOCS / page
    text = source.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if "://" in target or target.startswith("#"):
            continue
        destination = source.parent / target.split("#", maxsplit=1)[0]
        parent = destination.parent.resolve()
        assert parent.is_relative_to(DOCS), f"{page}: link leaves docs: {target}"
        if destination.exists():
            continue
        # The docs generator writes API reference pages from extra modules at build time.
        assert parent == DOCS / "extras" and destination.suffix == ".md", (page, target)
        assert (ROOT / "src/streamlit_extras" / destination.stem / "__init__.py").is_file(), (page, target)


def test_docs_styles_and_agent_index_are_published() -> None:
    config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    css = (DOCS / "assets/custom.css").read_text(encoding="utf-8")
    agent_index = (DOCS / "llms.txt").read_text(encoding="utf-8")

    assert "- assets/custom.css" in config
    assert "- md_in_html" in config
    assert "@media (max-width:" in css
    assert '[data-md-color-scheme="slate"]' in css
    assert "[Agent guide](https://arnaudmiribel.github.io/streamlit-extras/agents/)" in agent_index
    assert "[Browse extras](https://arnaudmiribel.github.io/streamlit-extras/extras/)" in agent_index
    assert "{% block announce %}" not in (ROOT / "overrides/main.html").read_text(encoding="utf-8")
