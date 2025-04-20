"""Build a Python package based on `uv`"""

import argparse
from pathlib import Path

from .core import build_pyckage


def main():
    parser = argparse.ArgumentParser(
        prog=__package__,
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "project_path", type=Path, help="The path to the project directory."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="The path to the output directory. Defaults to the project path.",
    )
    parser.add_argument("--debug", action="store_true", help="Debug mode")

    args = parser.parse_args()
    # print(args)
    # return

    if args.debug:
        import logging

        logging.basicConfig(level=logging.DEBUG)

    project_path: Path = args.project_path
    output_path: Path | None = args.output

    try:
        filepath = build_pyckage(project_path, output_path)
        if filepath is not None:
            print(f"Package created at\n  {filepath}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
