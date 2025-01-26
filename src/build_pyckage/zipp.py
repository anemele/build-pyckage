import zipfile
from pathlib import Path
from typing import Iterable

from returns.result import Failure, Result, Success

from .dep import PackageInfo, prepare_files

OUTPUT_DIR = Path("pyckage")
if not OUTPUT_DIR.exists():
    OUTPUT_DIR.mkdir()
if not (OUTPUT_DIR / ".gitignore").exists():
    (OUTPUT_DIR / ".gitignore").write_text("*")


def _create_zip(path: Path, info_list: Iterable[PackageInfo]) -> Result[None, str]:
    if path.exists():
        return Failure(f"File {path} already exists")
    with zipfile.ZipFile(path, "w") as zf:
        for info in info_list:
            zf.write(info.join(), arcname=info.rel)
    return Success(None)


def create_zip() -> Result[None, str]:
    try:
        package, info_list = prepare_files()
    except Exception as e:
        return Failure(str(e))
    # for info in info_list:
    #     print(info.join())
    filename = f"{package.name}-{package.version}.zip"
    return _create_zip(OUTPUT_DIR / filename, info_list)
