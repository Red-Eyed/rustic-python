"""Link the generated skill into Codex without overwriting existing installations."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from tools.bundle import ROOT, build_bundles


class InstallSettings(BaseSettings, frozen=True):
    """Read the installation destination from SKILLS_DIR or the user default."""

    model_config = SettingsConfigDict(extra="forbid")
    skills_dir: Path = Field(default_factory=lambda: Path.home() / ".agents/skills")


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
    settings = InstallSettings()
    print("Building the offline Rustic Python skill...")
    source = build_bundles(ROOT, ROOT / "build")
    target = install_skill(source, settings.skills_dir.expanduser())
    print(f"Installed {target} -> {source}")


if __name__ == "__main__":
    main()
