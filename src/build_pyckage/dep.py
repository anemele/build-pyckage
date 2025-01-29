from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import Iterable, Iterator, Optional

from .parser import Package, Project


@dataclass
class PathInfo:
    pre: Path
    rel: str

    def join(self):
        return self.pre / self.rel


SITE_PACKAGES = ".venv/Lib/site-packages"


def read_record(root: Path, package: Package) -> Iterable[PathInfo]:
    site_root = root / SITE_PACKAGES
    pkg_path = site_root / package.dist_info()
    if not pkg_path.exists():
        package.to_snake_case()
        pkg_path = site_root / package.dist_info()

    lines = (pkg_path / "RECORD").read_text().splitlines()
    for line in lines:
        path, *_ = line.split(",", 1)
        if path.startswith(".."):
            continue
        yield PathInfo(site_root, path)


def get_files(root: Path, packages: Iterable[Package]) -> Iterator[PathInfo]:
    for package in packages:
        yield from read_record(root, package)


def prepare_files(root: Path, project: Project) -> Optional[Iterator[PathInfo]]:
    deps = project.dependencies[1:]

    def get_this_files(root: Path):
        root = root / "src"
        for top, _, files in root.walk():
            if top.name == "__pycache__":
                continue
            for file in files:
                rel = (top / file).relative_to(root)
                yield PathInfo(root, str(rel))

    return chain(get_this_files(root), get_files(root, deps))
