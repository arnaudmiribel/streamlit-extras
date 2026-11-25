"""Point shadcn's git history lookup at the source of generated references."""

from pathlib import Path

from mkdocs.plugins import event_priority
from mkdocs.structure.pages import Page

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src" / "streamlit_extras"
DOCS_ROOT = Path(__file__).resolve().parent
_source_paths: dict[str, str] = {}


@event_priority(100)
def on_page_markdown(markdown: str, *, page: Page, **kwargs: object) -> str:
    if getattr(page.file, "generated_by", None) == "mkdocs-gen-files" and page.file.src_path.startswith(
        ("extras/", "extras_deprecated/")
    ):
        # Pages that gen-files only appends to (e.g. extras/index.md) keep their docs/ source
        source = DOCS_ROOT / page.file.src_path
        if not source.is_file():
            source = SOURCE_ROOT / Path(page.file.src_path).stem / "__init__.py"
        if source.is_file():
            _source_paths[page.file.src_path] = page.file.abs_src_path
            # The generated Markdown lives outside the git worktree; shadcn's
            # git timestamp lookup expects a path inside it.
            page.file.abs_src_path = str(source)
    return markdown


@event_priority(-100)
def on_page_content(html: str, *, page: Page, **kwargs: object) -> str:
    original_path = _source_paths.pop(page.file.src_path, None)
    if original_path is not None:
        page.file.abs_src_path = original_path
    return html
