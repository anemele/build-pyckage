"""Build a Python package based on `uv`"""

import argparse
from pathlib import Path

from .core import create_zip


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "package_path",
        type=Path,
        nargs="?",
        default=Path(),
        help="The directory containing the package to build",
    )
    args = parser.parse_args()
    package_path: Path = args.package_path

    try:
        filepath = create_zip(package_path)
        if filepath is not None:
            print(f"Package created at\n  {filepath}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
