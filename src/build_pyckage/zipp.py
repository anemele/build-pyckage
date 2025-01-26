import zipfile
from pathlib import Path
from typing import Iterable

from .dep import PackageInfo, prepare_files

OUTPUT_DIR = Path("pyckage")
if not OUTPUT_DIR.exists():
    OUTPUT_DIR.mkdir()
if not (gitignore := OUTPUT_DIR / ".gitignore").exists():
    gitignore.write_text("*")


def _create_zip(path: Path, info_list: Iterable[PackageInfo]):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        alreay_added = set()
        for info in info_list:
            if info.rel in alreay_added:
                continue
            alreay_added.add(info.rel)
            zf.write(info.join(), arcname=info.rel)


def create_zip(package_path: Path) -> Path:
    package, info_list = prepare_files(package_path)

    # get python version by reading `.python-version` by `uv`
    py_ver_file = package_path / ".python-version"
    if py_ver_file.exists():
        py_ver = py_ver_file.read_text().strip()
    else:
        py_ver = "0.0"

    filename = f"{package.name}-{package.version}-py{py_ver}.zip"
    filepath = OUTPUT_DIR / filename
    _create_zip(filepath, info_list)
    return filepath
