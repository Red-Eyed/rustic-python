#!/bin/sh
# Use upstream prebuilt binaries so readers do not need a Rust toolchain.
set -eu
cd "$(dirname "$0")/.."
version=0.5.4
case "$(uname -s)-$(uname -m)" in
    Darwin-arm64) target=aarch64-apple-darwin ;;
    Darwin-x86_64) target=x86_64-apple-darwin ;;
    Linux-x86_64) target=x86_64-unknown-linux-musl ;;
    Linux-aarch64) target=aarch64-unknown-linux-musl ;;
    *) echo "Unsupported platform: install mdBook $version and run mdbook build." >&2; exit 1 ;;
esac
directory="build/tools/mdbook-$version-$target"
if [ ! -x "$directory/mdbook" ]; then
    mkdir -p "$directory"
    archive="$directory/download.tar.gz"
    echo "Downloading mdBook $version for $target..."
    curl --fail --location --show-error --output "$archive" \
        "https://github.com/rust-lang/mdBook/releases/download/v$version/mdbook-v$version-$target.tar.gz"
    tar -xzf "$archive" -C "$directory" mdbook
fi
exec "$directory/mdbook" "$@"
