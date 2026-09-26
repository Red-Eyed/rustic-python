"""Package maintained sources for mdBook and an offline Codex skill."""

import re
import shutil
from pathlib import Path

from tools.skill_metadata import write_metadata

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "INSTALL.md",
    "pyproject.toml",
    "uv.lock",
    "pyrefly.toml",
    "ruff.toml",
    "pytest.ini",
)


def copy_sources(root: Path, destination: Path) -> None:
    """Copy only public guide sources, omitting caches and maintenance instructions."""
    destination.mkdir(parents=True)
    for name in FILES:
        shutil.copy2(root / name, destination / name)
    for name in ("docs", "examples", "tests"):
        shutil.copytree(
            root / name,
            destination / name,
            ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", "test_distribution.py"
            ),
        )
    readme = destination / "README.md"
    lines = readme.read_text().splitlines(keepends=True)
    readme.write_text(
        "".join(line for line in lines if not line.startswith("- [AGENTS.md]"))
    )


def book_summary(source: str) -> str:
    """Resolve the docs-relative reading order within the staged repository layout."""

    def rewrite(match: re.Match[str]) -> str:
        """Move a chapter link from docs-relative to repository-relative form."""
        path = match[1]
        relative = (
            path.removeprefix("../") if path.startswith("../") else f"docs/{path}"
        )
        return f"]({relative.replace('README.md', 'index.md')})"

    return re.sub(r"\]\(([^)]+)\)", rewrite, source)


def prepare_book_links(book: Path) -> None:
    """Use mdBook's index convention and link directory listings to GitHub."""
    (book / "README.md").rename(book / "index.md")
    for page in book.rglob("*.md"):
        page.write_text(book_page(page, book))


def book_page(page: Path, book: Path) -> str:
    """Adapt one page's links without changing its source in the repository."""
    text = page.read_text().replace("../README.md)", "../index.md)")

    def rewrite(match: re.Match[str]) -> str:
        """Keep file links local while directing directory browsing to GitHub."""
        link = match[1]
        if ":" in link or not link.endswith("/"):
            return match[0]
        destination = (page.parent / link).resolve()
        relative = destination.relative_to(book.resolve()).as_posix()
        return f"](https://github.com/Red-Eyed/rustic-python/tree/main/{relative})"

    return re.sub(r"\]\(([^)]+)\)", rewrite, text)


def build_bundles(root: Path, output: Path) -> Path:
    """Build fresh book sources and a standalone skill; return its directory."""
    book = output / "book-source"
    skill = output / "skills" / "rustic-python"
    for destination in (book, skill):
        if destination.exists():
            shutil.rmtree(destination)
        copy_sources(root, destination)
    prepare_book_links(book)
    (book / "SUMMARY.md").write_text(
        book_summary((root / "docs/SUMMARY.md").read_text())
    )
    shutil.copy2(root / "skills/rustic-python/SKILL.md", skill / "SKILL.md")
    write_metadata(root, skill)
    downloads = book / "downloads"
    downloads.mkdir()
    shutil.make_archive(
        str(downloads / "rustic-python"), "zip", skill.parent, skill.name
    )
    return skill


def main() -> None:
    """Build both distributions in the repository's ignored build directory."""
    skill = build_bundles(ROOT, ROOT / "build")
    print(f"Built book sources and skill: {skill}")


if __name__ == "__main__":
    main()
