#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

BAZELISK_VERSION="1.21.0"
BAZELISK_URL="https://github.com/bazelbuild/bazelisk/releases/download/v${BAZELISK_VERSION}/bazelisk-linux-amd64"
INSTALL_DIR="${HOME}/.local/bin"

if ! command -v bazel >/dev/null 2>&1; then
  mkdir -p "$INSTALL_DIR"
  curl -fsSL "$BAZELISK_URL" -o "$INSTALL_DIR/bazel"
  chmod +x "$INSTALL_DIR/bazel"
fi

export PATH="$INSTALL_DIR:$PATH"

bazel --version
