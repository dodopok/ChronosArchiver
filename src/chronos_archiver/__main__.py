"""Command-line interface entry point."""

import sys

from chronos_archiver.cli import cli


def main() -> int:
    """Main entry point for CLI."""
    return cli()


if __name__ == "__main__":
    sys.exit(main())