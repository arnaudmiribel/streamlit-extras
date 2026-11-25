import json
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
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


class MarkdownPayloadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_payload = False
        self.payload = ""
        self.button_found = False
        self.status_found = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "script" and attributes.get("id") == "extras-page-markdown":
            self.in_payload = True
        if tag == "button" and "extras-copy-page" in (attributes.get("class") or ""):
            self.button_found = attributes.get("type") == "button"
        if attributes.get("id") == "extras-copy-status":
            self.status_found = attributes.get("role") == "status" and attributes.get("aria-live") == "polite"

    def handle_data(self, data: str) -> None:
        if self.in_payload:
            self.payload += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self.in_payload = False


def test_docs_theme_has_compact_navigation_and_readable_accents() -> None:
    config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    css = (DOCS / "assets/custom.css").read_text(encoding="utf-8")
    home = (DOCS / "index.md").read_text(encoding="utf-8")
    template = (ROOT / "overrides/main.html").read_text(encoding="utf-8")

    assert "name: material" in config
    assert "navigation.expand" not in config
    assert "- Browse extras: extras/index.md" in config
    assert "- Extras reference: extras/" in config
    assert config.index("- For AI agents: agents.md") < config.index("- Extras reference: extras/")
    assert "extras-eyebrow" not in home
    assert "extras-page-tools__label" not in template
    assert "text-transform: uppercase" not in css
    assert "border-top:" not in css
    assert "border-bottom:" not in css
    path_rules = css.split(".md-typeset .extras-path {", maxsplit=1)[1].split("}", maxsplit=1)[0]
    assert "border: 1px solid var(--extras-border);" not in path_rules
    assert '[data-md-color-scheme="default"]' in css
    assert '[data-md-color-scheme="slate"]' in css


def test_built_docs_copy_source_is_markdown(tmp_path: Path) -> None:
    pytest.importorskip("mkdocs")
    site_dir = tmp_path / "site"
    subprocess.run(
        [sys.executable, "-m", "mkdocs", "build", "--strict", "--site-dir", str(site_dir)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    for expected, rendered in (
        ((DOCS / "getting_started.md").read_text(encoding="utf-8"), site_dir / "getting_started/index.html"),
        ("# Small additions. Better apps.", site_dir / "index.html"),
        ("# ", site_dir / "extras/stoggle/index.html"),
    ):
        parser = MarkdownPayloadParser()
        html = rendered.read_text(encoding="utf-8")
        parser.feed(html)
        markdown = json.loads(parser.payload)
        assert expected in markdown
        assert "Copy page as Markdown" in html
        assert parser.button_found and parser.status_found
    assert (site_dir / "assets/copy-page.js").is_file()

    home_html = (site_dir / "index.html").read_text(encoding="utf-8")
    reference_html = (site_dir / "extras/stoggle/index.html").read_text(encoding="utf-8")
    catalog_html = (site_dir / "extras/index.html").read_text(encoding="utf-8")
    for page_html in (home_html, catalog_html, reference_html):
        assert 'data-md-color-scheme="default"' in page_html
        assert 'data-md-color-scheme="slate"' in page_html
        assert "Browse extras" in page_html and "Extras reference" in page_html
        assert "Contributing" in page_html and "For AI agents" in page_html
    assert reference_html.index("For AI agents") < reference_html.index("Extras reference")
    assert "extras-eyebrow" not in home_html
    assert "➡️\u00a0\u00a0\u00a0Toggle button" in reference_html
    assert "streamlit_extras.stoggle import stoggle" in reference_html


def test_copy_payload_escapes_script_breakout() -> None:
    jinja2 = pytest.importorskip("jinja2")
    template = (ROOT / "overrides/main.html").read_text(encoding="utf-8")
    payload_template = re.search(r'<script type="application/json" id="extras-page-markdown">(.*?)</script>', template)
    assert payload_template is not None
    markdown = '</script><script>alert("injected")</script> & <tag>'
    rendered = (
        jinja2.Environment(autoescape=True).from_string(payload_template.group(1)).render(page={"markdown": markdown})
    )
    assert "</script>" not in rendered.lower()
    assert json.loads(rendered) == markdown


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not available")
def test_copy_page_click_copies_markdown_and_reports_clipboard_failure() -> None:
    script = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(process.argv[1], 'utf8');
let handler;
let copied;
let shouldFail = false;
const status = { textContent: '' };
const markdown = '# Title\n\n<unsafe>&';
const payload = { id: 'extras-page-markdown', textContent: JSON.stringify(markdown) };
const tools = { querySelector: () => status, nextElementSibling: payload };
const button = { closest: () => tools };
const document = { addEventListener: (event, callback) => { assert.equal(event, 'click'); handler = callback; } };
const navigator = { clipboard: { writeText: async (text) => {
  if (shouldFail) throw new Error('blocked');
  copied = text;
} } };
vm.runInNewContext(source, { document, navigator, JSON });
(async () => {
  await handler({ target: { closest: () => button } });
  assert.equal(copied, markdown);
  assert.equal(status.textContent, 'Markdown copied');
  shouldFail = true;
  await handler({ target: { closest: () => button } });
  assert.match(status.textContent, /Could not copy/);
})().catch(error => { console.error(error); process.exitCode = 1; });
"""
    subprocess.run(
        ["node", "-e", script, str(DOCS / "assets/copy-page.js")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
