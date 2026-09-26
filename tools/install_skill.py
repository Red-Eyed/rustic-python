"""Link the generated skill into Codex without overwriting existing installations."""

import os
from pathlib import Path

from tools.bundle import ROOT, build_bundles


def install_skill(source: Path, skills_directory: Path) -> Path:
    """Create an idempotent local link; reject any conflicting destination."""
    target = skills_directory / "rustic-python"
    if target.is_symlink() and target.resolve() == source.resolve():
        return target
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Refusing to replace an existing skill: {target}")
    skills_directory.mkdir(parents=True, exist_ok=True)
    target.symlink_to(source.resolve(), target_is_directory=True)
    return target


def main() -> None:
    """Build and install for the user, or into the explicit SKILLS_DIR location."""
    directory = Path(os.environ.get("SKILLS_DIR", str(Path.home() / ".agents/skills")))
    print("Building the offline Rustic Python skill...")
    source = build_bundles(ROOT, ROOT / "build")
    target = install_skill(source, directory.expanduser())
    print(f"Installed {target} -> {source}")


if __name__ == "__main__":
    main()
