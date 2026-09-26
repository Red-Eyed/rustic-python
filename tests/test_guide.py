"""Verify guide synchronization, executable examples, and static rejections."""

import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = sorted((ROOT / "examples").glob("*.py"))
PYTEST_EXAMPLES = sorted((ROOT / "tests" / "pytest_patterns").glob("*.py"))
DOCUMENTS = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
REJECTION = re.compile(r"# rejected\[([\w,-]+)\]: (.+)")


@dataclass(frozen=True)
class RejectedCase:
    """Bind an invalid line to its expected diagnostic kinds and source file."""

    path: Path
    line_number: int
    replacement: str
    error_kinds: tuple[str, ...]

    @property
    def name(self) -> str:
        """Identify the example and mutation in pytest's progress output."""
        return f"{self.path.stem}:{self.line_number}"


def rejected_cases() -> list[RejectedCase]:
    """Collect explicitly marked negative cases from the executable examples."""
    cases: list[RejectedCase] = []
    for path in EXAMPLES:
        for number, line in enumerate(path.read_text().splitlines(), start=1):
            match = REJECTION.fullmatch(line)
            if match is not None:
                cases.append(
                    RejectedCase(path, number, match[2], tuple(match[1].split(",")))
                )
    return cases


REJECTED_CASES = rejected_cases()


@pytest.fixture(scope="session")
def pyrefly() -> Path:
    """Resolve the checker supplied by the project's development environment."""
    executable = shutil.which("pyrefly")
    assert executable is not None, "Run tests through uv run pytest"
    return Path(executable)


def check_source(
    pyrefly: Path, tmp_path: Path, source: str
) -> subprocess.CompletedProcess[str]:
    """Check an isolated module against the repository's strict configuration."""
    path = tmp_path / "example.py"
    path.write_text(source)
    return subprocess.run(
        [
            str(pyrefly),
            "check",
            "--config",
            str(ROOT / "pyrefly.toml"),
            "--output-format",
            "min-text",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


def assert_rejected(
    result: subprocess.CompletedProcess[str], expected: set[tuple[int, str]]
) -> None:
    """Require the exact error locations and kinds, not just a failing process."""
    output = result.stdout + result.stderr
    assert result.returncode == 1, output
    found = re.findall(r"^ERROR .*?:(\d+):.* \[([\w-]+)\]$", result.stdout, re.M)
    assert {(int(line), kind) for line, kind in found} == expected, output


def documented_source_paths(document: Path) -> set[Path]:
    """Verify a page's Python fences and resolve their source paths relative to it."""
    markdown = document.read_text()
    linked = re.findall(
        r"\[Source\]\(((?:\.\./)?(?:examples|tests)/[\w/]+\.py)\)"
        r"\n\n```python\n(.*?)```",
        markdown,
        re.S,
    )
    assert len(linked) == markdown.count("```python\n"), document
    paths: set[Path] = set()
    for relative_path, code in linked:
        path = (document.parent / relative_path).resolve()
        assert path not in paths, f"Duplicate source snippet in {document}: {path}"
        assert path.read_text() == code, f"Outdated snippet in {document}: {path}"
        paths.add(path)
    return paths


def test_documentation_matches_examples() -> None:
    """Require the entry point and docs pages to cover each executable example."""
    assert EXAMPLES, "The guide must contain executable examples"
    paths: set[Path] = set()
    for document in DOCUMENTS:
        page_paths = documented_source_paths(document)
        assert paths.isdisjoint(page_paths), f"Duplicate source snippets in {document}"
        paths.update(page_paths)
    assert set(EXAMPLES) <= paths
    assert set(PYTEST_EXAMPLES) <= paths


def test_examples_declare_valid_rejection_cases() -> None:
    """Require every example to include well-formed static rejection cases."""
    assert {case.path for case in REJECTED_CASES} == set(EXAMPLES)
    for path in EXAMPLES:
        for line in path.read_text().splitlines():
            if line.startswith("# rejected"):
                assert REJECTION.fullmatch(line), f"Malformed rejection in {path}"


@pytest.mark.parametrize("path", EXAMPLES, ids=[path.stem for path in EXAMPLES])
def test_example_checks_and_runs(path: Path, pyrefly: Path, tmp_path: Path) -> None:
    """Verify each positive example both independently type-checks and executes."""
    result = check_source(pyrefly, tmp_path, path.read_text())
    assert result.returncode == 0, result.stdout + result.stderr
    executed = subprocess.run(
        [sys.executable, str(path)],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert executed.returncode == 0, executed.stdout + executed.stderr


@pytest.mark.parametrize(
    "case", REJECTED_CASES, ids=[case.name for case in REJECTED_CASES]
)
def test_invalid_example_is_rejected(
    case: RejectedCase, pyrefly: Path, tmp_path: Path
) -> None:
    """Uncomment one invalid operation and require only its documented errors."""
    lines = case.path.read_text().splitlines()
    lines[case.line_number - 1] = case.replacement
    result = check_source(pyrefly, tmp_path, "\n".join(lines) + "\n")
    assert_rejected(result, {(case.line_number, kind) for kind in case.error_kinds})


def test_new_variant_breaks_incomplete_match(pyrefly: Path, tmp_path: Path) -> None:
    """Adding a split must expose the now-incomplete exhaustive dispatcher."""
    source = (ROOT / "examples" / "exhaustive_matching.py").read_text()
    original = 'Split: TypeAlias = Literal["train", "validation", "test"]'
    extended = 'Split: TypeAlias = Literal["train", "validation", "test", "holdout"]'
    assert source.count(original) == 1
    changed = source.replace(original, extended)
    line = changed.splitlines().index("            assert_never(split)") + 1
    result = check_source(pyrefly, tmp_path, changed)
    assert_rejected(result, {(line, "bad-argument-type")})


@pytest.fixture
def unguarded_mapping_source() -> str:
    """Remove only the workaround to reproduce the pinned checker's limitation."""
    source = (ROOT / "examples" / "checker_limits.py").read_text()
    guard = (
        "    if not isinstance(payload, Mapping):\n"
        '        raise ValueError("expected a mapping")\n'
    )
    assert source.count(guard) == 1
    return source.replace(guard, "")


def test_boolean_predicate_needs_a_narrowing_contract(
    pyrefly: Path, tmp_path: Path
) -> None:
    """A boolean-returning helper does not communicate its runtime type check."""
    source = (ROOT / "examples" / "checker_limits.py").read_text()
    source = source.replace("-> TypeGuard[str]:", "-> bool:")
    line = source.splitlines().index("        return value.strip()") + 1
    result = check_source(pyrefly, tmp_path, source)
    assert_rejected(result, {(line, "missing-attribute")})


def test_mapping_pattern_exposes_a_checker_limitation(
    pyrefly: Path, tmp_path: Path, unguarded_mapping_source: str
) -> None:
    """Record valid Python rejected by Pyrefly 1.3.1, so upgrades trigger review."""
    source = unguarded_mapping_source + '\nassert name == "training"\n'
    line = source.splitlines().index('        case {"name": str(name)}:') + 1
    result = check_source(pyrefly, tmp_path, source)
    assert_rejected(result, {(line, "not-callable")})
    executed = subprocess.run(
        [sys.executable, str(tmp_path / "example.py")],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert executed.returncode == 0, executed.stdout + executed.stderr


def test_scoped_suppression_keeps_unrelated_errors_visible(
    pyrefly: Path, tmp_path: Path, unguarded_mapping_source: str
) -> None:
    """Demonstrate a fallback suppression in isolation, not in application code."""
    pattern = '        case {"name": str(name)}:'
    suppressed = unguarded_mapping_source.replace(
        pattern, "        # pyrefly: ignore[not-callable]\n" + pattern
    )
    result = check_source(pyrefly, tmp_path, suppressed)
    assert result.returncode == 0, result.stdout + result.stderr
    broken = suppressed + '\ncount: int = "not a count"\n'
    result = check_source(pyrefly, tmp_path, broken)
    assert_rejected(result, {(len(broken.splitlines()), "bad-assignment")})


def test_incorrect_vendor_stub_can_be_repaired_locally(
    pyrefly: Path, tmp_path: Path
) -> None:
    """An inaccurate stub can reject working Python; repair metadata, not callers."""
    (tmp_path / "vendor.py").write_text(
        '"""Simulate an installed SDK whose behavior is known."""\n'
        'def output_name():\n    """Return the documented output name."""\n'
        '    return "embedding"\n'
    )
    stub = tmp_path / "vendor.pyi"
    stub.write_text("def output_name() -> int: ...\n")
    client = tmp_path / "client.py"
    client.write_text(
        "from vendor import output_name\nname: str = output_name()\n"
        'assert name == "embedding"\n'
    )
    command = [
        str(pyrefly),
        "check",
        "--config",
        str(ROOT / "pyrefly.toml"),
        "--search-path",
        str(tmp_path),
        "--output-format",
        "min-text",
        str(client),
    ]
    rejected = subprocess.run(command, capture_output=True, text=True, timeout=30)
    assert_rejected(rejected, {(2, "bad-assignment")})
    stub.write_text("def output_name() -> str: ...\n")
    accepted = subprocess.run(command, capture_output=True, text=True, timeout=30)
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr
    executed = subprocess.run(
        [sys.executable, str(client)], capture_output=True, text=True, timeout=30
    )
    assert executed.returncode == 0, executed.stdout + executed.stderr
