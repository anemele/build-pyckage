import sys
import zipfile
from dataclasses import dataclass
from importlib.metadata import PackagePath
from pathlib import Path
from typing import Iterator, Optional

from .dep import get_dep_files, get_src_files
from .parser import Project, get_project


@dataclass
class ZipItem:
    info: zipfile.ZipInfo
    data: bytes | str


LIB_PREFIX = "lib"


def _gen_items(
    project: Project,
    src_root: Path,
    src_files: Iterator[Path],
    dep_files: Iterator[PackagePath],
):
    for file in src_files:
        yield ZipItem(
            zipfile.ZipInfo(f"{LIB_PREFIX}/{file}"),
            src_root.joinpath(file).read_bytes(),
        )

    for file in dep_files:
        yield ZipItem(zipfile.ZipInfo(f"{LIB_PREFIX}/{file}"), file.read_binary())

    python = f"@call %~dp0{LIB_PREFIX}\\python.exe"
    yield ZipItem(zipfile.ZipInfo("python.bat"), f"{python} %*")

    for name, script in project.scripts.items():
        module_name, func_name = script.split(":", 1)
        yield ZipItem(
            zipfile.ZipInfo(f"{name}.bat"),
            f"{python} -c "
            f"\"import sys;sys.argv[0]='%~n0';from {module_name} import {func_name};sys.exit({func_name}())\""
            " %*\n"
            "@exit /b %errorlevel%\n",
        )


def _create_zip(path: Path, items: Iterator[ZipItem]):
    with zipfile.ZipFile(path, "w") as zf:
        for item in items:
            zf.writestr(item.info, item.data, compress_type=zipfile.ZIP_DEFLATED)


def build_pyckage(
    project_path: Path, output_path: Optional[Path] = None
) -> Optional[Path]:
    """If build finished return the pyckage path, else None"""

    # Get info from the pyproject.toml file
    project = get_project(project_path)
    if project is None:
        print(f"Failed to read pyproject.toml: {project_path.resolve()}")
        return None

    sys.path.insert(0, str(project_path / ".venv/Lib/site-packages"))
    src_files = get_src_files(project_path)
    dep_files = get_dep_files(project)

    # this line may need to be changed
    py_ver = project_path.joinpath(".python-version").read_text().strip()
    filename = f"{project.name}-{project.version}-pyckage-py{py_ver}.zip"

    if output_path is None:
        output_path = project_path / "dist"
    output_path.mkdir(parents=True, exist_ok=True)

    filepath = output_path / filename
    zip_items = _gen_items(project, project_path / "src", src_files, dep_files)
    _create_zip(filepath, zip_items)

    return filepath
