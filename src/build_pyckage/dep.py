import re
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


def read_record(pkg_path: Path) -> Iterable[PathInfo]:
    lines = (pkg_path / "RECORD").read_text().splitlines()
    for line in lines:
        path, *_ = line.split(",", 1)
        if path.startswith(".."):
            continue
        yield PathInfo(pkg_path.parent, path)


SITE_PACKAGES = ".venv/Lib/site-packages"
META_PTN = re.compile(r"Name: ([\w_-]+)\nVersion: ([\w\.]+)\n")


def _get_package_mapping(root: Path) -> Iterator[tuple[Package, Path]]:
    meta_it = (root / SITE_PACKAGES).glob("*.dist-info/METADATA")
    for meta in meta_it:
        sg = META_PTN.search(meta.read_text(encoding="utf-8"))
        if sg is None:
            # should not happen
            continue
        name = sg.group(1)
        version = sg.group(2)
        yield Package(name, version), meta.parent


def get_files(root: Path, packages: Iterable[Package]) -> Iterator[PathInfo]:
    mapping = _get_package_mapping(root)
    mapping = dict(mapping)
    for package in packages:
        yield from read_record(mapping[package])


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
