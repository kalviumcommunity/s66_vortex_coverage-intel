"""Parse, clean, and chunk approved documents from the corpus directory.

Phase: phase-02-ingestion.md
"""

from __future__ import annotations

import argparse


def main() -> int:
    """Parse, clean, and chunk approved documents from the corpus directory."""
    parser = argparse.ArgumentParser(description="Parse, clean, and chunk approved documents from the corpus directory.")
    parser.parse_args()
    raise SystemExit(
        "Not yet implemented — see phases/phase-02-ingestion.md\n"
        "Run `make help` for available targets."
    )


if __name__ == "__main__":
    raise SystemExit(main())
