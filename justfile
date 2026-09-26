default:
    @just --list

check:
    uv run --locked ruff check .
    uv run --locked ruff format --check .
    uv run --locked pyrefly check
    uv run --locked pytest

bundle:
    uv run --locked -m tools.bundle

book: bundle
    sh tools/mdbook.sh build
    uv run --locked -m tools.check_book

serve: bundle
    sh tools/mdbook.sh serve --open

install-skill:
    uv run --locked -m tools.install_skill
