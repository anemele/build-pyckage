from importlib.metadata import PackagePath, distribution
from itertools import chain
from pathlib import Path
from typing import Iterator

from .parser import Project


def get_src_files(root: Path) -> Iterator[Path]:
    root = root / "src"
    for top, _, files in root.walk():
        if top.name == "__pycache__":
            continue
        for file in files:
            rel = top.joinpath(file).relative_to(root)
            yield rel


def _get_dep_files(pkg: str) -> Iterator[PackagePath]:
    dist = distribution(pkg)
    if dist.files is None:
        return
    for file in dist.files:
        s = file.as_posix()
        if s.startswith(".."):
            continue
        yield file


def get_dep_files(project: Project) -> Iterator[PackagePath]:
    deps = project.dependencies
    return chain.from_iterable(map(_get_dep_files, deps))
