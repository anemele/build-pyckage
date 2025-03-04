import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from .config import load_config
from .dep import PathInfo, prepare_files
from .embed import prepare_embedded_python
from .parser import Project, get_project

LIB_PREFIX = "lib"
BIN_PREFIX = "bin"


@dataclass
class ZipItem:
    info: zipfile.ZipInfo
    data: bytes | str


def _gen_items(
    project: Project,
    info_list: Iterable[PathInfo],
    embed_zip: zipfile.ZipFile,
):
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

    for name, script in project.scripts.items():
        module_name = script.split(":", 1)[0]
        yield ZipItem(
            zipfile.ZipInfo(f"{name}.bat"),
            f"@%~dp0{BIN_PREFIX}\\python.exe -m {module_name} %*",
        )


def _create_zip(path: Path, items: Iterable[ZipItem]):
    with zipfile.ZipFile(path, "w") as zf:
        for item in items:
            zf.writestr(item.info, item.data, compress_type=zipfile.ZIP_DEFLATED)


def create_zip(package_path: Path) -> Optional[Path]:
    project = get_project(package_path)
    if project is None:
        print(f"Failed to read pyproject.toml: {package_path.resolve()}")
        return None

    info_list = prepare_files(package_path, project)
    if info_list is None:
        print(f"No dependencies found in {package_path.resolve()}")
        return None

    config = load_config()

    # this line may need to be changed
    py_ver = (package_path / ".python-version").read_text().strip()
    filename = f"{project.name}-{project.version}-py{py_ver}.zip"
    filepath = config.pyckage_path / filename
    embed_zip = prepare_embedded_python(py_ver, config)
    if embed_zip is None:
        return None

    zip_items = _gen_items(project, info_list, embed_zip)
    _create_zip(filepath, zip_items)

    return filepath
