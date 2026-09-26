"""Check rendered local links and anchors, including downloadable source files."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from typing_extensions import override

from tools.bundle import ROOT


class PageLinks(HTMLParser):
    """Collect link destinations and named anchors from a rendered HTML page."""

    def __init__(self) -> None:
        """Initialize one page's independent link and anchor collections."""
        super().__init__()
        self.links: list[str] = []
        self.anchors: set[str] = set()

    @override
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Record navigation and asset references without executing page scripts."""
        for name, value in attrs:
            if value is None:
                continue
            if name in ("href", "src"):
                self.links.append(value)
            if name == "id":
                self.anchors.add(value)


def check_book(site: Path) -> list[str]:
    """Return broken local file or HTML-anchor references under a built site."""
    site = site.resolve()
    pages: dict[Path, PageLinks] = {}
    for path in site.rglob("*.html"):
        parser = PageLinks()
        parser.feed(path.read_text())
        pages[path] = parser
    if not pages:
        return [f"No HTML pages found in {site}"]
    errors: list[str] = []
    for path, page in pages.items():
        for link in page.links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc:
                continue
            target = local_target(site, path, unquote(parsed.path))
            if not target.is_relative_to(site) or not target.is_file():
                errors.append(f"{path.relative_to(site)}: missing file {link}")
                continue
            anchor = unquote(parsed.fragment)
            if anchor and target in pages and anchor not in pages[target].anchors:
                errors.append(f"{path.relative_to(site)}: missing anchor {link}")
    return errors


def local_target(site: Path, page: Path, link: str) -> Path:
    """Resolve relative URLs and the GitHub Pages project prefix."""
    if not link:
        return page
    if link.startswith("/"):
        target = site / link.removeprefix("/rustic-python/").lstrip("/")
    else:
        target = page.parent / link
    if target.is_dir():
        target /= "index.html"
    return target.resolve()


def main() -> None:
    """Fail the build when generated navigation or source downloads are broken."""
    errors = check_book(ROOT / "build/book")
    if errors:
        raise SystemExit("\n".join(errors))
    print("Rendered book links and anchors are valid")


if __name__ == "__main__":
    main()
