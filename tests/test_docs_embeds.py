"""Rendered documentation checks for interactive example embeds."""

import html
import re
import subprocess
import sys
from html.parser import HTMLParser
from importlib import metadata
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

ROOT = Path(__file__).resolve().parents[1]


class ExampleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[tuple[str, dict[str, str | None]]] = []
        self.examples: list[tuple[dict[str, str | None], dict[str, str | None]]] = []
        self.links: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "iframe" and attributes.get("id", "").startswith("iframe-"):
            self.examples.append((attributes, self.stack[-1][1]))
            assert any(
                parent_tag == "details" and parent.get("class") == "extras-example" for parent_tag, parent in self.stack
            )
        if tag == "a" and any(parent.get("class") == "extras-example-footer" for _, parent in self.stack):
            self.links.append(attributes)
        if tag not in {"meta", "link", "img", "input", "br", "hr", "source"}:
            self.stack.append((tag, attributes))

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break


@pytest.fixture(scope="module")
def rendered_site(tmp_path_factory: pytest.TempPathFactory) -> Path:
    pytest.importorskip("mkdocs")
    site = tmp_path_factory.mktemp("stlite-site")
    result = subprocess.run(
        [sys.executable, "-m", "mkdocs", "build", "--strict", "--site-dir", str(site)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return site


def test_rendered_example_is_contained_and_resizes(rendered_site: Path) -> None:
    page = (rendered_site / "extras/stoggle/index.html").read_text(encoding="utf-8")
    parser = ExampleParser()
    parser.feed(page)

    assert len(parser.examples) == 1
    iframe, parent = parser.examples[0]
    assert parent.get("class") == "extras-example-frame"
    assert iframe["title"] == "Interactive example: example"
    assert iframe["loading"] == "lazy"
    assert iframe["height"] == "400"
    source = html.unescape(iframe["srcdoc"] or "")
    assert 'id="root"' in source
    assert "@stlite/browser@1.8.1/build/stlite.css" in source
    assert "@stlite/browser@1.8.1/build/stlite.js" in source
    version = metadata.version("streamlit-extras")
    assert re.search(
        rf'requirements: \["https://files\.pythonhosted\.org/packages/[^\"]+/streamlit_extras-{re.escape(version)}-py3-none-any\.whl"\]',
        source,
    )
    assert 'requirements: ["streamlit", "streamlit-extras"]' not in source
    assert 'entrypoint: "streamlit_app.py"' in source
    assert "example()" in source
    assert re.search(r'iFrameResize\(\{[^}]*\}, "#iframe-example"\)', page)
    assert "iframeResizer.min.js" in page


def test_multiple_examples_have_distinct_frames_and_resize_targets(rendered_site: Path) -> None:
    page = (rendered_site / "extras/badges/index.html").read_text(encoding="utf-8")
    parser = ExampleParser()
    parser.feed(page)

    frame_ids = [iframe["id"] for iframe, _ in parser.examples]
    assert frame_ids == [
        "iframe-example_pypi",
        "iframe-example_streamlit",
        "iframe-example_github",
        "iframe-example_twitter",
        "iframe-example_buymeacoffee",
    ]
    for frame_id in frame_ids:
        assert page.count(f'"#{frame_id}"') == 1
        assert page.count(f'id="{frame_id}"') == 1
        assert re.search(r'iFrameResize\(\{[^}]*\}, "#' + frame_id + r'"\)', page)


def test_rendered_example_links_are_html_safe(rendered_site: Path) -> None:
    page = (rendered_site / "extras/stoggle/index.html").read_text(encoding="utf-8")
    parser = ExampleParser()
    parser.feed(page)

    assert len(parser.links) == 2
    assert parser.links[0]["href"] == "https://github.com/whitphx/stlite"
    playground = urlsplit(parser.links[1]["href"] or "")
    assert (playground.scheme, playground.netloc, playground.path) == ("https", "streamlit.io", "/playground")
    assert set(parse_qs(playground.query)) == {"template", "code"}
    assert parse_qs(playground.query)["template"] == ["blank"]
    assert re.fullmatch(r"[A-Za-z0-9_-]+", parse_qs(playground.query)["code"][0])
    assert "?template=blank&amp;code=" in page


def test_example_styles_scope_both_themes_without_inline_legacy_styles(rendered_site: Path) -> None:
    page = (rendered_site / "extras/stoggle/index.html").read_text(encoding="utf-8")
    css = (rendered_site / "assets/custom.css").read_text(encoding="utf-8")

    marker = '<details class="extras-example">'
    assert marker in page
    assert "<style>" not in page[page.index(marker) : page.index("</details>", page.index(marker))]
    assert re.search(r":root\s*\{[^}]*--extras-border: #[0-9a-f]+;", css)
    assert re.search(r"\.dark\s*\{[^}]*--extras-border: #[0-9a-f]+;", css)
    assert ".typography .extras-example-frame iframe {" in css
    assert "width: 100%;" in css[css.index(".typography .extras-example-frame iframe {") :]
    assert ".typography .extras-example-footer a:focus-visible" in css
