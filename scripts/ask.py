"""Ask a coverage question from the command line.

Phase: phase-05-rag-core.md
"""

from __future__ import annotations

import argparse


def main() -> int:
    """Ask a coverage question from the command line."""
    parser = argparse.ArgumentParser(description="Ask a coverage question from the command line.")
    parser.parse_args()
    raise SystemExit(
        "Not yet implemented — see phases/phase-05-rag-core.md\n"
        "Run `make help` for available targets."
    )


if __name__ == "__main__":
    raise SystemExit(main())
