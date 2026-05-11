#!/usr/bin/env bash
set -euo pipefail

check_markitdown() {
    python3 -m markitdown --version 2>/dev/null
}

install_markitdown() {
    echo "Installing markitdown..." >&2
    if python3 -m pip install markitdown; then
        return 0
    fi
    echo "python3 -m pip failed, trying pip3..." >&2
    if pip3 install markitdown; then
        return 0
    fi
    echo "Error: failed to install markitdown. Please install it manually:" >&2
    echo "  python3 -m pip install markitdown" >&2
    exit 1
}

main() {
    local version
    version=$(check_markitdown)
    if [[ -n "$version" ]]; then
        echo "markitdown OK (v${version})"
        exit 0
    fi

    echo "markitdown not found, installing..." >&2
    install_markitdown

    version=$(check_markitdown)
    if [[ -n "$version" ]]; then
        echo "markitdown OK (v${version})"
        exit 0
    fi

    echo "Error: markitdown installation completed but command still not available." >&2
    exit 1
}

main
