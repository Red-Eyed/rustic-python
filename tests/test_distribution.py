"""Verify portable skill content, book navigation, and safe local installation."""

import re
from pathlib import Path
from zipfile import ZipFile

import pytest

from tools.bundle import ROOT, build_bundles
from tools.check_book import check_book
from tools.install_skill import install_skill


@pytest.fixture
def skill(tmp_path: Path) -> Path:
    """Build both distributions outside the checkout."""
    return build_bundles(ROOT, tmp_path / "build")


def test_skill_is_self_contained(skill: Path) -> None:
    """Require local Markdown references to resolve without the original checkout."""
    for page in skill.rglob("*.md"):
        text = re.sub(r"```.*?```", "", page.read_text(), flags=re.S)
        text = re.sub(r"`[^`]+`", "", text)
        for link in re.findall(r"\]\(([^)]+)\)", text):
            if ":" in link or link.startswith("#"):
                continue
            destination = (page.parent / link.split("#")[0]).resolve()
            assert destination.is_relative_to(skill), (page, link)
            assert destination.exists(), (page, link)
    assert not list(skill.rglob("AGENTS.md"))
    assert not list(skill.rglob("__pycache__"))
    assert not (skill / "tests/test_distribution.py").exists()
    assert (skill / "examples/third_party_boundary.py").read_bytes() == (
        ROOT / "examples/third_party_boundary.py"
    ).read_bytes()


def test_archive_preserves_skill_layout(skill: Path) -> None:
    """The downloadable archive must extract into one complete skill folder."""
    archive = skill.parents[1] / "book-source/downloads/rustic-python.zip"
    with ZipFile(archive) as bundle:
        assert (
            bundle.read("rustic-python/SKILL.md") == (skill / "SKILL.md").read_bytes()
        )
        assert all(name.startswith("rustic-python/") for name in bundle.namelist())


def test_book_lists_all_chapters(skill: Path) -> None:
    """Prevent a new topic from silently disappearing from the online book."""
    source = skill.parents[1] / "book-source"
    links = re.findall(r"\]\(([^)]+)\)", (source / "SUMMARY.md").read_text())
    assert len(links) == len(set(links))
    for link in links:
        assert (source / link).is_file(), link
    chapters = {f"docs/{page.name}" for page in (ROOT / "docs").glob("*.md")}
    assert chapters - {"docs/SUMMARY.md"} <= set(links)


def test_install_is_idempotent_and_tracks_rebuilds(skill: Path, tmp_path: Path) -> None:
    """An installed link must keep working when generated references are refreshed."""
    directory = tmp_path / "user-skills"
    target = install_skill(skill, directory)
    assert install_skill(skill, directory) == target
    assert target.is_symlink()
    build_bundles(ROOT, skill.parents[1])
    assert (target / "SKILL.md").read_bytes() == (skill / "SKILL.md").read_bytes()


def test_install_preserves_existing_directory(skill: Path, tmp_path: Path) -> None:
    """Never replace an independently installed or user-edited skill."""
    directory = tmp_path / "user-skills"
    existing = directory / "rustic-python"
    existing.mkdir(parents=True)
    marker = existing / "custom.txt"
    marker.write_text("keep")
    with pytest.raises(FileExistsError, match="Refusing to replace"):
        install_skill(skill, directory)
    assert marker.read_text() == "keep"


def test_install_preserves_unrelated_symlink(skill: Path, tmp_path: Path) -> None:
    """Reject conflicting links even if their destination no longer exists."""
    directory = tmp_path / "user-skills"
    directory.mkdir()
    existing = directory / "rustic-python"
    existing.symlink_to(tmp_path / "missing")
    with pytest.raises(FileExistsError, match="Refusing to replace"):
        install_skill(skill, directory)
    assert existing.is_symlink()


@pytest.fixture
def site(tmp_path: Path) -> Path:
    """Create a rendered page with an anchor and a downloadable source file."""
    (tmp_path / "index.html").write_text('<h1 id="intro">Introduction</h1>')
    (tmp_path / "example.py").write_text("value = 1\n")
    return tmp_path


@pytest.mark.parametrize(
    ("link", "valid"),
    [
        ("index.html#intro", True),
        ("/rustic-python/index.html#intro", True),
        ("example.py", True),
        ("https://example.com/external", True),
        ("missing.html", False),
        ("index.html#missing", False),
        ("../outside.html", False),
    ],
)
def test_rendered_link_validation(site: Path, link: str, valid: bool) -> None:
    """Catch broken files, fragments, and escaping paths without fetching externals."""
    (site / "chapter.html").write_text(f'<a href="{link}">Read</a>')
    assert (not check_book(site)) == valid
