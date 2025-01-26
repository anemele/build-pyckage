import zipfile
from pathlib import Path
from typing import Iterable

from .dep import PackageInfo, prepare_files

OUTPUT_DIR = Path("pyckage")
if not OUTPUT_DIR.exists():
    OUTPUT_DIR.mkdir()
if not (OUTPUT_DIR / ".gitignore").exists():
    (OUTPUT_DIR / ".gitignore").write_text("*")


def _create_zip(path: Path, info_list: Iterable[PackageInfo]):
    with zipfile.ZipFile(path, "w") as zf:
        for info in info_list:
            zf.write(info.join(), arcname=info.rel)


def create_zip(package_path: str) -> Path:
    package, info_list = prepare_files(package_path)
    # for info in info_list:
    #     print(info.join())

    # get python version by reading `.python-version` by `uv`
    py_ver_file = Path(".python-version")
    if not py_ver_file.exists():
        py_ver = "0.0"
    else:
        py_ver = py_ver_file.read_text().strip()

    filename = f"{package.name}-{package.version}-py{py_ver}.zip"
    filepath = OUTPUT_DIR / filename
    _create_zip(filepath, info_list)
    return filepath
