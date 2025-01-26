import zipfile
from pathlib import Path
from typing import Iterable

from .dep import PackageInfo, prepare_files

OUTPUT_DIR = "pyckage"


def ensure_output(path: Path):
    if not path.exists():
        path.mkdir()
    if not (gitignore := path / ".gitignore").exists():
        gitignore.write_text("*")


def _create_zip(path: Path, info_list: Iterable[PackageInfo]):
    with zipfile.ZipFile(path, "w") as zf:
        alreay_added = set()
        for info in info_list:
            if info.rel in alreay_added:
                continue
            alreay_added.add(info.rel)

            zf.writestr(
                zipfile.ZipInfo(info.rel),
                info.join().read_bytes(),
                compress_type=zipfile.ZIP_DEFLATED,
            )


def create_zip(package_path: Path) -> Path:
    package, info_list = prepare_files(package_path)

    # get python version by reading `.python-version` by `uv`
    py_ver_file = package_path / ".python-version"
    if py_ver_file.exists():
        py_ver = py_ver_file.read_text().strip()
    else:
        py_ver = "0.0"

    filename = f"{package.name}-{package.version}-py{py_ver}.zip"
    output_path = package_path / OUTPUT_DIR
    ensure_output(output_path)
    filepath = output_path / filename
    _create_zip(filepath, info_list)
    return filepath
