import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from .dep import PackageInfo, prepare_files
from .embed import prepare_embedded_python
from .utils import ensure_path

OUTPUT_DIR = "pyckage"


LIB_PREFIX = "lib"
BIN_PREFIX = "bin"


@dataclass
class ZipItem:
    info: zipfile.ZipInfo
    data: bytes | str


def _gen_items(info_list: Iterable[PackageInfo], embed_zip: Optional[zipfile.ZipFile]):
    alreay_added = set()
    for info in info_list:
        if info.rel in alreay_added:
            continue
        alreay_added.add(info.rel)

        yield ZipItem(
            zipfile.ZipInfo(f"{LIB_PREFIX}/{info.rel}"), info.join().read_bytes()
        )

    if embed_zip is None:
        return

    for info in embed_zip.infolist():
        if info.filename.endswith("._pth"):
            continue
        yield ZipItem(
            zipfile.ZipInfo(f"{BIN_PREFIX}/{info.filename}"),
            embed_zip.read(info.filename),
        )

    yield ZipItem(zipfile.ZipInfo(f"{BIN_PREFIX}/{LIB_PREFIX}.pth"), f"../{LIB_PREFIX}")
    yield ZipItem(zipfile.ZipInfo("python.bat"), f"@%~dp0{BIN_PREFIX}\\python.exe %*")


def _create_zip(path: Path, items: Iterable[ZipItem]):
    with zipfile.ZipFile(path, "w") as zf:
        for item in items:
            zf.writestr(item.info, item.data, compress_type=zipfile.ZIP_DEFLATED)


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
    ensure_path(output_path)
    filepath = output_path / filename
    zip_items = _gen_items(info_list, prepare_embedded_python(py_ver))
    _create_zip(filepath, zip_items)

    return filepath
