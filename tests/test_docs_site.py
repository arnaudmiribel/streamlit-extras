import importlib.util
import json
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace

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
    assert "dark" in css
    assert "[Agent guide](https://arnaudmiribel.github.io/streamlit-extras/agents/)" in agent_index
    assert "[Browse extras](https://arnaudmiribel.github.io/streamlit-extras/extras/)" in agent_index
    assert "{% block announce %}" not in (ROOT / "overrides/main.html").read_text(encoding="utf-8")


def test_docs_publish_builds_strictly_before_deploying() -> None:
    workflow = (ROOT / ".github/workflows/publish_docs.yml").read_text(encoding="utf-8")
    requirements = (DOCS / "requirements.txt").read_text(encoding="utf-8")

    assert "mkdocs-shadcn==" in requirements
    assert "mkdocs-material" not in requirements
    assert "mkdocs-shadcn-" in workflow
    assert workflow.index("mkdocs build --strict") < workflow.index("mkdocs gh-deploy --force")


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
    template = (ROOT / "overrides/templates/page.html").read_text(encoding="utf-8")

    assert "name: shadcn" in config
    assert "icon: assets/logo.png" in config
    assert "navigation.expand" not in config
    assert "- Browse extras: extras/index.md" in config
    assert "- Extras reference: extras/" in config
    assert config.index("- For AI agents: agents.md") < config.index("- Extras reference: extras/")
    assert config.index("- Extras reference: extras/") < config.index("- Deprecated extras: extras_deprecated/")
    assert "extras-hero" in home
    assert "extras-copy-page" in template
    assert (
        template.index('id="page-header"')
        < template.index('class="extras-page-tools"')
        < template.index("{{ page.content }}")
    )
    assert ".extras-copy-page" in css
    assert "dark" in css


def test_built_docs_copy_source_is_markdown(tmp_path: Path) -> None:
    pytest.importorskip("mkdocs")
    site_dir = tmp_path / "site"
    result = subprocess.run(
        [sys.executable, "-m", "mkdocs", "build", "--strict", "--site-dir", str(site_dir)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    for expected, rendered in (
        ((DOCS / "getting_started.md").read_text(encoding="utf-8"), site_dir / "getting_started/index.html"),
        ("# Small additions. Better apps.", site_dir / "index.html"),
        ("*Submitted by Arnaud Miribel*", site_dir / "extras/stoggle/index.html"),
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
    getting_started_html = (site_dir / "getting_started/index.html").read_text(encoding="utf-8")
    reference_html = (site_dir / "extras/stoggle/index.html").read_text(encoding="utf-8")
    catalog_html = (site_dir / "extras/index.html").read_text(encoding="utf-8")
    for page_html in (home_html, getting_started_html, catalog_html, reference_html):
        assert re.search(r'src="(?:\.\./)*js/dark\.js"', page_html)
        assert 'title="Toggle theme"' in page_html
        assert re.search(r'<img[^>]+src="(?:\.\./)*assets/logo\.png"[^>]*>', page_html)
        assert "Browse extras" in page_html and "Extras reference" in page_html
        assert "Contributing" in page_html and "For AI agents" in page_html
        assert page_html.index("Extras reference") < page_html.index("Deprecated extras")
        assert (
            page_html.index("<article")
            < page_html.index('class="extras-page-tools"')
            < page_html.index('class="typography')
        )
    assert reference_html.index("For AI agents") < reference_html.index("Extras reference")
    assert "extras-eyebrow" not in home_html
    assert re.search(r'<h1 class="scroll-m-20[^>]*>\s*Stoggle\s*</h1>', reference_html)
    assert "streamlit_extras.stoggle import stoggle" in reference_html
    for page_html in (getting_started_html, reference_html):
        assert re.search(r'<link id="pygments-light"[^>]*href="[^"]*css/pygments/shadcn-light.css"', page_html)
        assert re.search(r'<link id="pygments-dark"[^>]*href="[^"]*css/pygments/github-dark.css"', page_html)
    assert (site_dir / "css/pygments/shadcn-light.css").is_file()
    assert (site_dir / "css/pygments/github-dark.css").is_file()
    assert ".codehilite .kn" in (site_dir / "css/pygments/shadcn-light.css").read_text(encoding="utf-8")
    assert re.search(r'<div class="language-bash codehilite"><pre>.*?<code>', getting_started_html, re.DOTALL)
    assert re.search(
        r'<div class="language-python codehilite"><pre>.*?<code>.*?<span class="kn">',
        getting_started_html,
        re.DOTALL,
    )
    assert re.search(
        r'<div class="language-python codehilite"><pre>.*?<code>.*?<span class="kn">', reference_html, re.DOTALL
    )
    assert '<h2 id="summary">' not in reference_html
    assert reference_html.count('id="functions"') == 1
    assert reference_html.count('class="scroll-m-20 text-4xl') == 1
    assert not re.search(r'<div class="typography[^>]*>\s*<h1', reference_html)
    assert reference_html.index("Submitted by Arnaud Miribel") < reference_html.index('id="functions"')


def test_generated_reference_timestamp_uses_git_source_and_restores_virtual_path() -> None:
    pytest.importorskip("mkdocs")
    spec = importlib.util.spec_from_file_location("shadcn_compat_test", DOCS / "shadcn_compat.py")
    assert spec is not None and spec.loader is not None
    compat = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(compat)

    for path in ("extras/stoggle.md", "extras_deprecated/stoggle.md"):
        generated_file = SimpleNamespace(
            generated_by="mkdocs-gen-files",
            src_path=path,
            abs_src_path=f"/tmp/mkdocs-generated/{path}",
        )
        page = SimpleNamespace(file=generated_file)
        original = generated_file.abs_src_path
        assert compat.on_page_markdown("# Stoggle", page=page) == "# Stoggle"
        assert generated_file.abs_src_path == str(ROOT / "src/streamlit_extras/stoggle/__init__.py")
        assert compat.on_page_content("<h1>Stoggle</h1>", page=page) == "<h1>Stoggle</h1>"
        assert generated_file.abs_src_path == original

    ordinary = SimpleNamespace(
        file=SimpleNamespace(generated_by=None, src_path="extras/stoggle.md", abs_src_path="/docs/stoggle.md")
    )
    assert compat.on_page_markdown("ordinary", page=ordinary) == "ordinary"
    assert ordinary.file.abs_src_path == "/docs/stoggle.md"
    missing = SimpleNamespace(
        file=SimpleNamespace(
            generated_by="mkdocs-gen-files", src_path="extras/not_an_extra.md", abs_src_path="/tmp/missing.md"
        )
    )
    assert compat.on_page_markdown("missing", page=missing) == "missing"
    assert missing.file.abs_src_path == "/tmp/missing.md"


def test_copy_payload_escapes_script_breakout() -> None:
    jinja2 = pytest.importorskip("jinja2")
    template = (ROOT / "overrides/templates/page.html").read_text(encoding="utf-8")
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
