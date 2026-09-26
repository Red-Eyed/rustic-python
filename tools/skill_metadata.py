"""Record bundle provenance and file hashes for agent-managed updates."""

import hashlib
import subprocess
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

METADATA_FILE = "rustic-python-source.json"
Revision = Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class SourceRevision(BaseModel, frozen=True):
    """Identify a Git revision without claiming uncommitted edits belong to it."""

    model_config = ConfigDict(strict=True, extra="forbid")
    commit: Revision
    dirty: bool


class SkillMetadata(BaseModel, frozen=True):
    """Describe the reference snapshot; file hashes detect edits, not authenticity."""

    model_config = ConfigDict(strict=True, extra="forbid")
    schema_version: Literal[1] = 1
    repository: Literal["https://github.com/Red-Eyed/rustic-python"] = (
        "https://github.com/Red-Eyed/rustic-python"
    )
    source: SourceRevision
    files: dict[str, Digest]


def git_output(root: Path, *arguments: str) -> str:
    """Read Git state from a checkout, raising if Git cannot establish provenance."""
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def source_revision(root: Path) -> SourceRevision:
    """Capture HEAD and tracked or untracked edits; ignored build files do not count."""
    return SourceRevision(
        commit=git_output(root, "rev-parse", "HEAD"),
        dirty=bool(git_output(root, "status", "--porcelain", "--untracked-files=all")),
    )


def file_hashes(directory: Path) -> dict[str, str]:
    """Hash bundle files, excluding this manifest and generated Python/test caches."""
    ignored = {"__pycache__", ".pytest_cache", ".ruff_cache"}
    hashes: dict[str, str] = {}
    for path in sorted(directory.rglob("*")):
        relative = path.relative_to(directory)
        if ignored.intersection(relative.parts) or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            raise ValueError(f"Unexpected symlink in skill: {relative}")
        if path.is_file() and relative.as_posix() != METADATA_FILE:
            hashes[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def write_metadata(root: Path, skill: Path) -> None:
    """Write revision and content metadata after all skill files have been staged."""
    metadata = SkillMetadata(source=source_revision(root), files=file_hashes(skill))
    (skill / METADATA_FILE).write_text(metadata.model_dump_json(indent=2) + "\n")
